(() => {
  const dataElement = document.getElementById("design-data");
  const container = document.getElementById("design-map");
  if (!dataElement || !container) return;

  if (typeof maplibregl === "undefined") {
    container.innerHTML = '<div class="empty-state"><p>No se pudo cargar MapLibre.</p></div>';
    return;
  }

  const data = JSON.parse(dataElement.textContent);
  const map = new maplibregl.Map({
    container: "design-map",
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
    zoom: 19,
  });

  map.addControl(new maplibregl.NavigationControl(), "top-right");
  map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");

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

  map.on("load", () => {
    if (data.roof) {
      map.addSource("roof", {
        type: "geojson",
        data: { type: "Feature", geometry: asGeometry(data.roof), properties: {} },
      });
      map.addLayer({
        id: "roof-fill",
        type: "fill",
        source: "roof",
        paint: { "fill-color": "#0f2a44", "fill-opacity": 0.08 },
      });
      map.addLayer({
        id: "roof-line",
        type: "line",
        source: "roof",
        paint: { "line-color": "#0f2a44", "line-width": 2 },
      });
    }

    if (data.layout) {
      map.addSource("panels", { type: "geojson", data: data.layout });
      map.addLayer({
        id: "panels-fill",
        type: "fill",
        source: "panels",
        paint: { "fill-color": "#0d9488", "fill-opacity": 0.82 },
      });
      map.addLayer({
        id: "panels-line",
        type: "line",
        source: "panels",
        paint: { "line-color": "#ecfdf5", "line-width": 0.7 },
      });
    }

    const geometry = asGeometry(data.layout) || asGeometry(data.roof);
    if (geometry) {
      const bounds = new maplibregl.LngLatBounds();
      extendBounds(bounds, geometry.coordinates || []);
      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, { padding: 50, maxZoom: 20, duration: 500 });
      }
    }

    map.on("click", "panels-fill", (event) => {
      const feature = event.features && event.features[0];
      if (!feature) return;
      const panel = feature.properties && feature.properties.panel;
      new maplibregl.Popup()
        .setLngLat(event.lngLat)
        .setHTML(`<strong>Módulo ${panel || ""}</strong>`)
        .addTo(map);
    });
    map.on("mouseenter", "panels-fill", () => {
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", "panels-fill", () => {
      map.getCanvas().style.cursor = "";
    });
  });
})();
