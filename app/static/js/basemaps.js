/**
 * Capas base compartidas por el mapa de emplazamiento y el mapa de diseño.
 *
 * No se usa map.setStyle(): cambiar el estilo eliminaría las capas de
 * techumbre, obstáculos, paneles y handles. En su lugar todas las capas base
 * viven en el estilo y se alterna su visibilidad.
 */
(() => {
  const STORAGE_KEY = "fv-basemap";
  const DEFAULT_KEY = "hybrid";

  const SOURCES = {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      maxzoom: 19,
      attribution: "© OpenStreetMap contributors",
    },
    "esri-imagery": {
      type: "raster",
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      ],
      tileSize: 256,
      maxzoom: 19,
      attribution: "Esri, Maxar, Earthstar Geographics, GIS User Community",
    },
    "esri-labels": {
      type: "raster",
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      ],
      tileSize: 256,
      maxzoom: 19,
      attribution: "Esri",
    },
    opentopo: {
      type: "raster",
      tiles: [
        "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
        "https://b.tile.opentopomap.org/{z}/{x}/{y}.png",
        "https://c.tile.opentopomap.org/{z}/{x}/{y}.png",
      ],
      tileSize: 256,
      maxzoom: 17,
      attribution: "© OpenStreetMap contributors, SRTM, © OpenTopoMap (CC-BY-SA)",
    },
  };

  const BASEMAPS = {
    streets: {
      label: "Calles",
      layers: ["basemap-osm"],
      sources: ["osm"],
    },
    satellite: {
      label: "Satélite",
      layers: ["basemap-esri-imagery"],
      sources: ["esri-imagery"],
    },
    hybrid: {
      label: "Híbrido",
      layers: ["basemap-esri-imagery", "basemap-esri-labels"],
      sources: ["esri-imagery", "esri-labels"],
    },
    topo: {
      label: "Topográfico",
      layers: ["basemap-opentopo"],
      sources: ["opentopo"],
    },
  };

  const PRIMARY_SOURCE = {
    streets: "osm",
    satellite: "esri-imagery",
    hybrid: "esri-imagery",
    topo: "opentopo",
  };

  const STYLE_LAYERS = [
    { id: "basemap-osm", type: "raster", source: "osm", layout: { visibility: "none" } },
    {
      id: "basemap-esri-imagery",
      type: "raster",
      source: "esri-imagery",
      layout: { visibility: "none" },
    },
    {
      id: "basemap-esri-labels",
      type: "raster",
      source: "esri-labels",
      layout: { visibility: "none" },
    },
    {
      id: "basemap-opentopo",
      type: "raster",
      source: "opentopo",
      layout: { visibility: "none" },
    },
  ];

  function readSavedKey() {
    try {
      const value = window.localStorage.getItem(STORAGE_KEY);
      return value && BASEMAPS[value] ? value : DEFAULT_KEY;
    } catch (_) {
      return DEFAULT_KEY;
    }
  }

  function saveKey(key) {
    try {
      window.localStorage.setItem(STORAGE_KEY, key);
    } catch (_) {
      /* localStorage puede estar bloqueado; no es crítico. */
    }
  }

  function buildStyle() {
    return {
      version: 8,
      sources: { ...SOURCES },
      layers: STYLE_LAYERS.map((layer) => ({ ...layer })),
    };
  }

  function applyBasemap(map, key) {
    const selected = BASEMAPS[key] ? key : DEFAULT_KEY;
    const activeLayers = new Set(BASEMAPS[selected].layers);
    STYLE_LAYERS.forEach((layer) => {
      if (!map.getLayer(layer.id)) return;
      map.setLayoutProperty(
        layer.id,
        "visibility",
        activeLayers.has(layer.id) ? "visible" : "none"
      );
    });
  }

  function init(map, selectElement) {
    let currentKey = readSavedKey();
    let fallbackApplied = false;

    if (selectElement) {
      selectElement.value = currentKey;
      selectElement.addEventListener("change", () => {
        currentKey = selectElement.value;
        saveKey(currentKey);
        applyBasemap(map, currentKey);
      });
    }

    const apply = () => applyBasemap(map, currentKey);
    if (map.loaded()) {
      apply();
    } else {
      map.once("load", apply);
    }

    map.on("error", (event) => {
      if (fallbackApplied || currentKey === "streets") return;
      const sourceId = event && event.sourceId;
      if (!sourceId) return;
      if (sourceId !== PRIMARY_SOURCE[currentKey]) return;
      fallbackApplied = true;
      currentKey = "streets";
      saveKey(currentKey);
      if (selectElement) selectElement.value = "streets";
      applyBasemap(map, currentKey);
    });
  }

  window.FVBasemaps = {
    BASEMAPS,
    buildStyle,
    init,
    applyBasemap,
    getCurrentKey: readSavedKey,
  };
})();
