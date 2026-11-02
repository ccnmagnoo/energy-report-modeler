"""Distribución automática de módulos sobre un polígono de techumbre.

La grilla se calcula en metros (UTM local) y luego se devuelve en WGS84. Esto
evita el error clásico de hacer buffers en grados, que en Chile equivalen a
decenas de kilómetros.
"""

from __future__ import annotations

from pyproj import Transformer
from shapely.geometry import box

from app.services.geometry import (
    as_polygon,
    feature,
    feature_collection,
    project_geometry,
    utm_epsg,
)


def _grid(
    polygon,
    panel_width: float,
    panel_height: float,
    gap: float = 0.05,
) -> list:
    inner = polygon.buffer(-0.25)
    if inner.is_empty:
        inner = polygon

    min_x, min_y, max_x, max_y = inner.bounds
    rectangles = []
    y = min_y
    while y + panel_height <= max_y + 1e-9:
        x = min_x
        while x + panel_width <= max_x + 1e-9:
            rectangle = box(x, y, x + panel_width, y + panel_height)
            if inner.contains(rectangle):
                rectangles.append(rectangle)
            x += panel_width + gap
        y += panel_height + gap
    return rectangles


def generate_layout(
    roof_geojson: str | dict,
    panel_width_m: float,
    panel_height_m: float,
    tilt_deg: float,
    usable_factor: float = 0.9,
    latitude: float = -33.45,
    longitude: float = -70.67,
) -> dict:
    """Genera una grilla de paneles y elige la orientación con más unidades.

    Es un layout conservador: los paneles deben quedar completamente dentro del
    polígono y se deja un retiro perimetral de 25 cm. La inclinación no altera
    la huella en planta del MVP; sí se usa más adelante en la simulación.
    """

    if panel_width_m <= 0 or panel_height_m <= 0:
        raise ValueError("Las dimensiones del panel deben ser positivas")

    polygon_wgs84 = as_polygon(roof_geojson)
    epsg = utm_epsg(latitude, longitude)
    forward = Transformer.from_crs("EPSG:4326", epsg, always_xy=True)
    inverse = Transformer.from_crs(epsg, "EPSG:4326", always_xy=True)
    polygon = project_geometry(polygon_wgs84, forward)
    roof_area = float(polygon.area)
    if roof_area <= 0:
        raise ValueError("La techumbre no tiene superficie válida")

    portrait = _grid(polygon, panel_width_m, panel_height_m)
    landscape = _grid(polygon, panel_height_m, panel_width_m)

    orientation = "retrato"
    rectangles = portrait
    if len(landscape) > len(portrait):
        orientation = "paisaje"
        rectangles = landscape

    features = []
    for index, rectangle in enumerate(rectangles, start=1):
        geographic = project_geometry(rectangle, inverse)
        features.append(
            feature(
                geographic,
                {
                    "panel": index,
                    "width_m": round(panel_width_m, 3),
                    "height_m": round(panel_height_m, 3),
                },
            )
        )

    count = len(features)
    panel_area = count * panel_width_m * panel_height_m
    occupancy = min(1.0, panel_area / roof_area) if roof_area else 0.0
    occupancy = occupancy * max(0.0, min(1.0, usable_factor))

    return {
        "geojson": feature_collection(features),
        "count": count,
        "orientation": orientation,
        "panel_area_m2": round(panel_area, 2),
        "roof_area_m2": round(roof_area, 2),
        "occupancy": round(occupancy, 4),
        "tilt_deg": tilt_deg,
    }
