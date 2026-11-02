(() => {
  const dataElement = document.getElementById("site-data");
  const container = document.getElementById("site-map");
  if (!dataElement || !container) return;

  if (typeof maplibregl === "undefined") {
    container.innerHTML = '<div class="empty-state"><p>No se pudo cargar MapLibre.</p></div>';
    return;
  }

  const data = JSON.parse(dataElement.textContent);
  const emptyCollection = { type: "FeatureCollection", features: [] };
  let mode = "roof";
  let coords = [];
  let drawing = true;
  let roofId = data.roofId || null;

  const map = new maplibregl.Map({
    container: "site-map",
    style: {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256,
          maxzoom: 19,
          attribution: "© OpenStreetMap contributors",
        },
      },
      layers: [{ id: "osm", type: "raster", source: "osm" }],
    },
    center: [data.longitude, data.latitude],
    zoom: 18,
  });

  map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
  map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
  map.doubleClickZoom.disable();

  const marker = new maplibregl.Marker({ color: "#0f766e" })
    .setLngLat([data.longitude, data.latitude])
    .addTo(map);

  function asGeometry(value) {
    if (!value) return null;
    return value.type === "Feature" ? value.geometry : value;
  }

  function extendBounds(bounds, value) {
    if (!Array.isArray(value)) return;
    if (typeof value[0] === "number" && typeof value[1] === "number") {
      bounds.extend(value);
      return;
    }
    value.forEach((item) => extendBounds(bounds, item));
  }

  function fitGeometry(geometry) {
    if (!geometry) return;
    const bounds = new maplibregl.LngLatBounds();
    extendBounds(bounds, geometry.coordinates || []);
    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, { padding: 50, maxZoom: 19, duration: 500 });
    }
  }

  function setSource(id, value) {
    const source = map.getSource(id);
    if (source) source.setData(value);
  }

  function renderDraft() {
    if (coords.length === 0) {
      setSource("draft", emptyCollection);
    } else if (coords.length < 3) {
      setSource("draft", {
        type: "Feature",
        geometry: { type: "LineString", coordinates: coords },
        properties: {},
      });
    } else {
      setSource("draft", {
        type: "Feature",
        geometry: {
          type: "Polygon",
          coordinates: [[...coords, coords[0]]],
        },
        properties: {},
      });
    }
    updateStatus();
  }

  function updateStatus() {
    const status = document.getElementById("draw-status");
    if (!status) return;
    if (coords.length === 0) {
      status.textContent = "Dibuja al menos 3 vértices.";
    } else if (coords.length < 3) {
      status.textContent = `${coords.length} vértice(s). Faltan ${3 - coords.length}.`;
    } else if (drawing) {
      status.textContent = `${coords.length} vértices. Doble clic para cerrar.`;
    } else {
      status.textContent = `${coords.length} vértices. Listo para guardar.`;
    }
  }

  function setMode(nextMode) {
    if (nextMode === "obstacle" && !roofId) {
      alert("Primero guarda la techumbre para poder agregar obstáculos.");
      return;
    }
    mode = nextMode;
    coords = [];
    drawing = true;
    document.querySelectorAll("[data-draw-mode]").forEach((button) => {
      button.classList.toggle("active", button.dataset.drawMode === mode);
    });
    renderDraft();
  }

  map.on("load", () => {
    map.addSource("roof", { type: "geojson", data: emptyCollection });
    map.addSource("obstacles", { type: "geojson", data: emptyCollection });
    map.addSource("draft", { type: "geojson", data: emptyCollection });

    map.addLayer({
      id: "roof-fill",
      type: "fill",
      source: "roof",
      paint: { "fill-color": "#0f766e", "fill-opacity": 0.18 },
    });
    map.addLayer({
      id: "roof-line",
      type: "line",
      source: "roof",
      paint: { "line-color": "#0f766e", "line-width": 2 },
    });
    map.addLayer({
      id: "obstacles-fill",
      type: "fill",
      source: "obstacles",
      paint: { "fill-color": "#d97706", "fill-opacity": 0.3 },
    });
    map.addLayer({
      id: "obstacles-line",
      type: "line",
      source: "obstacles",
      paint: { "line-color": "#b45309", "line-width": 1.5 },
    });
    map.addLayer({
      id: "draft-fill",
      type: "fill",
      source: "draft",
      paint: { "fill-color": "#2563eb", "fill-opacity": 0.12 },
    });
    map.addLayer({
      id: "draft-line",
      type: "line",
      source: "draft",
      paint: { "line-color": "#2563eb", "line-width": 2, "line-dasharray": [2, 1] },
    });

    const roofGeometry = asGeometry(data.roofGeojson);
    if (roofGeometry) {
      setSource("roof", {
        type: "Feature",
        geometry: roofGeometry,
        properties: {},
      });
      fitGeometry(roofGeometry);
    }

    if (data.obstacles && data.obstacles.length) {
      setSource("obstacles", {
        type: "FeatureCollection",
        features: data.obstacles.map((item) => ({
          type: "Feature",
          geometry: asGeometry(item.geojson),
          properties: { name: item.name, height_m: item.heightM, kind: item.kind },
        })),
      });
    }
    updateStatus();
  });

  map.on("click", (event) => {
    if (!drawing) return;
    if (event.originalEvent && event.originalEvent.detail > 1) return;
    coords.push([event.lngLat.lng, event.lngLat.lat]);
    renderDraft();
  });

  map.on("dblclick", (event) => {
    event.preventDefault();
    if (coords.length >= 3) {
      drawing = false;
      updateStatus();
    }
  });

  document.querySelectorAll("[data-draw-mode]").forEach((button) => {
    button.addEventListener("click", () => setMode(button.dataset.drawMode));
  });

  const clearButton = document.getElementById("clear-draw");
  if (clearButton) {
    clearButton.addEventListener("click", () => {
      coords = [];
      drawing = true;
      renderDraft();
    });
  }

  function polygonPayload() {
    if (coords.length < 3) {
      alert("Dibuja al menos 3 vértices.");
      return null;
    }
    return {
      name: document.getElementById("roof-name").value || "Techumbre principal",
      geojson: {
        type: "Polygon",
        coordinates: [[...coords, coords[0]]],
      },
      tilt_deg: Number(document.getElementById("roof-tilt").value || 20),
      azimuth_deg: Number(document.getElementById("roof-azimuth").value || 180),
      material: document.getElementById("roof-material").value,
      usable_factor: Number(document.getElementById("roof-usable").value || 0.9),
    };
  }

  async function sendJson(url, method, payload) {
    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (response.status === 401) {
      window.location.href = "/login";
      return null;
    }
    if (!response.ok) {
      let message = "No fue posible guardar.";
      try {
        const body = await response.json();
        message = body.detail || message;
      } catch (_) {
        /* noop */
      }
      throw new Error(message);
    }
    return response.json();
  }

  const saveRoofButton = document.getElementById("save-roof");
  if (saveRoofButton) {
    saveRoofButton.addEventListener("click", async () => {
      const payload = polygonPayload();
      if (!payload) return;
      saveRoofButton.disabled = true;
      try {
        const url = roofId ? `/api/roofs/${roofId}` : `/api/projects/${data.projectId}/roofs`;
        const result = await sendJson(url, roofId ? "PUT" : "POST", payload);
        if (result) {
          window.location.href = `/projects/${data.projectId}/site?notice=Techumbre+guardada`;
        }
      } catch (error) {
        alert(error.message);
        saveRoofButton.disabled = false;
      }
    });
  }

  const saveObstacleButton = document.getElementById("save-obstacle");
  if (saveObstacleButton) {
    saveObstacleButton.addEventListener("click", async () => {
      if (!roofId) {
        alert("Primero guarda la techumbre.");
        return;
      }
      if (coords.length < 3) {
        alert("Dibuja el polígono del obstáculo.");
        return;
      }
      saveObstacleButton.disabled = true;
      try {
        await sendJson(`/api/roofs/${roofId}/obstacles`, "POST", {
          name: document.getElementById("obstacle-name").value || "Obstáculo",
          geojson: { type: "Polygon", coordinates: [[...coords, coords[0]]] },
          height_m: Number(document.getElementById("obstacle-height").value || 1),
          kind: document.getElementById("obstacle-kind").value,
        });
        window.location.href = `/projects/${data.projectId}/site?notice=Obst%C3%A1culo+guardado`;
      } catch (error) {
        alert(error.message);
        saveObstacleButton.disabled = false;
      }
    });
  }

  const geocodeButton = document.getElementById("geocode-button");
  const geocodeResults = document.getElementById("geocode-results");
  if (geocodeButton && geocodeResults) {
    geocodeButton.addEventListener("click", async () => {
      const query = document.getElementById("address").value.trim();
      if (!query) return;
      geocodeButton.disabled = true;
      geocodeResults.innerHTML = '<span class="muted">Buscando…</span>';
      try {
        const response = await fetch(`/api/geocode?q=${encodeURIComponent(query)}`);
        if (response.status === 401) {
          window.location.href = "/login";
          return;
        }
        const body = await response.json();
        geocodeResults.innerHTML = "";
        if (body.error) {
          const message = document.createElement("span");
          message.className = "muted";
          message.textContent = body.error;
          geocodeResults.appendChild(message);
          return;
        }
        if (!body.results || !body.results.length) {
          const message = document.createElement("span");
          message.className = "muted";
          message.textContent = "Sin resultados. Ajusta la dirección o ingresa coordenadas manualmente.";
          geocodeResults.appendChild(message);
          return;
        }
        body.results.forEach((result) => {
          const button = document.createElement("button");
          button.type = "button";
          button.className = "geocode-item";
          button.textContent = result.display_name;
          button.addEventListener("click", () => {
            document.getElementById("latitude").value = Number(result.lat).toFixed(6);
            document.getElementById("longitude").value = Number(result.lon).toFixed(6);
            document.getElementById("address").value = result.display_name;
            marker.setLngLat([Number(result.lon), Number(result.lat)]);
            map.flyTo({ center: [Number(result.lon), Number(result.lat)], zoom: 18 });
            geocodeResults.innerHTML = "";
          });
          geocodeResults.appendChild(button);
        });
      } catch (error) {
        geocodeResults.innerHTML = "";
        const message = document.createElement("span");
        message.className = "muted";
        message.textContent = "No fue posible consultar el geocodificador.";
        geocodeResults.appendChild(message);
      } finally {
        geocodeButton.disabled = false;
      }
    });
  }
})();
