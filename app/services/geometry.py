"""Conversión y cálculo de geometrías GeoJSON."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
from pyproj import Transformer
from shapely import transform as shapely_transform
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.geometry.base import BaseGeometry


class GeometryError(ValueError):
    """GeoJSON inválido o geometría no soportada."""


def as_shape(geojson: dict[str, Any] | str) -> BaseGeometry:
    if isinstance(geojson, str):
        try:
            geojson = json.loads(geojson)
        except json.JSONDecodeError as exc:
            raise GeometryError("El GeoJSON no es válido") from exc

    if not isinstance(geojson, dict):
        raise GeometryError("Se esperaba un objeto GeoJSON")

    if geojson.get("type") == "Feature":
        geometry = geojson.get("geometry")
    else:
        geometry = geojson

    if not isinstance(geometry, dict):
        raise GeometryError("El GeoJSON no contiene una geometría")

    try:
        geom = shape(geometry)
    except (TypeError, ValueError, KeyError) as exc:
        raise GeometryError("No fue posible interpretar la geometría") from exc

    if geom.is_empty:
        raise GeometryError("La geometría está vacía")
    return geom


def as_polygon(geojson: dict[str, Any] | str) -> Polygon:
    geom = as_shape(geojson)
    if isinstance(geom, MultiPolygon):
        geom = max(geom.geoms, key=lambda item: item.area)
    if not isinstance(geom, Polygon):
        raise GeometryError("Se requiere un polígono")
    if len(geom.exterior.coords) < 4:
        raise GeometryError("El polígono debe tener al menos 3 vértices")
    if not geom.is_valid:
        raise GeometryError(
            "El polígono se auto-intersecta o no es válido; corrige los nodos."
        )
    if geom.area <= 0:
        raise GeometryError("El polígono no tiene superficie válida")
    return geom


def utm_epsg(latitude: float, longitude: float) -> str:
    zone = int((longitude + 180) / 6) + 1
    if latitude >= 0:
        return f"EPSG:326{zone:02d}"
    return f"EPSG:327{zone:02d}"


def project_geometry(geom: BaseGeometry, transformer: Transformer) -> BaseGeometry:
    """Proyecta una geometría usando una transformación pyproj."""

    def apply(coords):
        x, y = transformer.transform(coords[:, 0], coords[:, 1])
        return np.column_stack([x, y])

    return shapely_transform(geom, apply)


def area_m2(geojson: dict[str, Any] | str, latitude: float, longitude: float) -> float:
    polygon = as_polygon(geojson)
    transformer = Transformer.from_crs(
        "EPSG:4326", utm_epsg(latitude, longitude), always_xy=True
    )
    projected = project_geometry(polygon, transformer)
    return round(float(projected.area), 2)


def centroid_lonlat(geojson: dict[str, Any] | str) -> tuple[float, float]:
    point = as_shape(geojson).centroid
    return (float(point.x), float(point.y))


def to_geojson(geom: BaseGeometry) -> dict[str, Any]:
    return mapping(geom)


def feature(geom: BaseGeometry, properties: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": properties or {},
    }


def feature_collection(features: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": features}
