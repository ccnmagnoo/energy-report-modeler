from __future__ import annotations

import json

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import require_api_user
from app.config import USER_AGENT
from app.db import get_db
from app.models import Obstacle, Project, Roof, Site, User
from app.services.audit import log
from app.services.geometry import (
    GeometryError,
    area_m2,
    as_polygon,
    centroid_lonlat,
    feature_collection,
    to_geojson,
)

router = APIRouter(prefix="/api")


class RoofIn(BaseModel):
    name: str = Field(default="Techumbre principal", max_length=120)
    geojson: dict
    tilt_deg: float = 20
    azimuth_deg: float = 180
    material: str = "Techumbre metálica"
    usable_factor: float = 0.9


class ObstacleIn(BaseModel):
    name: str = Field(default="Obstáculo", max_length=120)
    geojson: dict
    height_m: float = 1.0
    kind: str = "otro"


@router.get("/geocode")
def geocode(
    q: str = Query("", min_length=0, max_length=250),
    user: User = Depends(require_api_user),
):
    if not q.strip():
        return {"results": []}
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": q.strip(),
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 5,
                "countrycodes": "cl",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        results = [
            {
                "display_name": item.get("display_name"),
                "lat": float(item.get("lat")),
                "lon": float(item.get("lon")),
                "type": item.get("type"),
            }
            for item in data
        ]
        return {"results": results}
    except (requests.RequestException, ValueError) as exc:
        return {"results": [], "error": f"No fue posible geocodificar: {exc}"}


@router.post("/projects/{project_id}/roofs")
def create_roof(
    project_id: int,
    payload: RoofIn,
    user: User = Depends(require_api_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    try:
        as_polygon(payload.geojson)
    except GeometryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    site = project.site
    if site is None:
        longitude, latitude = centroid_lonlat(payload.geojson)
        site = Site(
            project_id=project.id,
            address="Sin dirección",
            latitude=latitude,
            longitude=longitude,
        )
        db.add(site)
        db.flush()

    measured_area = area_m2(payload.geojson, site.latitude, site.longitude)
    roof = Roof(
        site_id=site.id,
        name=payload.name.strip() or "Techumbre principal",
        geom_geojson=json.dumps(payload.geojson),
        area_m2=measured_area,
        tilt_deg=payload.tilt_deg,
        azimuth_deg=payload.azimuth_deg,
        material=payload.material.strip() or "Techumbre metálica",
        usable_factor=max(0.1, min(1.0, payload.usable_factor)),
    )
    db.add(roof)
    db.flush()
    log(
        db,
        user,
        "roof",
        roof.id,
        "created",
        {"project_id": project.id, "area_m2": measured_area},
    )
    db.commit()
    return {"id": roof.id, "area_m2": roof.area_m2}


@router.put("/roofs/{roof_id}")
def update_roof(
    roof_id: int,
    payload: RoofIn,
    user: User = Depends(require_api_user),
    db: Session = Depends(get_db),
):
    roof = db.get(Roof, roof_id)
    if roof is None:
        raise HTTPException(status_code=404, detail="Techumbre no encontrada")
    try:
        as_polygon(payload.geojson)
    except GeometryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    site = roof.site
    measured_area = area_m2(payload.geojson, site.latitude, site.longitude)
    roof.name = payload.name.strip() or roof.name
    roof.geom_geojson = json.dumps(payload.geojson)
    roof.area_m2 = measured_area
    roof.tilt_deg = payload.tilt_deg
    roof.azimuth_deg = payload.azimuth_deg
    roof.material = payload.material.strip() or roof.material
    roof.usable_factor = max(0.1, min(1.0, payload.usable_factor))
    log(db, user, "roof", roof.id, "updated", {"area_m2": measured_area})
    db.commit()
    return {"id": roof.id, "area_m2": roof.area_m2}


@router.post("/roofs/{roof_id}/obstacles")
def create_obstacle(
    roof_id: int,
    payload: ObstacleIn,
    user: User = Depends(require_api_user),
    db: Session = Depends(get_db),
):
    roof = db.get(Roof, roof_id)
    if roof is None:
        raise HTTPException(status_code=404, detail="Techumbre no encontrada")
    try:
        as_polygon(payload.geojson)
    except GeometryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    obstacle = Obstacle(
        roof_id=roof.id,
        name=payload.name.strip() or "Obstáculo",
        geom_geojson=json.dumps(payload.geojson),
        height_m=max(0.0, payload.height_m),
        kind=payload.kind.strip() or "otro",
    )
    db.add(obstacle)
    db.flush()
    log(db, user, "obstacle", obstacle.id, "created", {"roof_id": roof.id})
    db.commit()
    return {"id": obstacle.id}


@router.get("/projects/{project_id}/export.geojson")
def export_geojson(
    project_id: int,
    user: User = Depends(require_api_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.site is None:
        return feature_collection([])

    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [project.site.longitude, project.site.latitude],
            },
            "properties": {
                "element": "site",
                "name": project.name,
                "address": project.site.address,
                "comuna": project.site.comuna,
            },
        }
    ]
    for roof in project.site.roofs:
        try:
            geometry = to_geojson(as_polygon(roof.geom_geojson))
        except GeometryError:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "element": "roof",
                    "id": roof.id,
                    "name": roof.name,
                    "area_m2": roof.area_m2,
                    "tilt_deg": roof.tilt_deg,
                    "azimuth_deg": roof.azimuth_deg,
                },
            }
        )
        for obstacle in roof.obstacles:
            try:
                obstacle_geometry = to_geojson(as_polygon(obstacle.geom_geojson))
            except GeometryError:
                continue
            features.append(
                {
                    "type": "Feature",
                    "geometry": obstacle_geometry,
                    "properties": {
                        "element": "obstacle",
                        "id": obstacle.id,
                        "name": obstacle.name,
                        "height_m": obstacle.height_m,
                        "roof_id": roof.id,
                    },
                }
            )
    return JSONResponse(feature_collection(features), media_type="application/geo+json")
