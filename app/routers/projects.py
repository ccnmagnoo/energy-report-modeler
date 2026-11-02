from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_user
from app.db import get_db
from app.models import Design, Document, Equipment, Project, Roof, Site, User
from app.routers.utils import percent, to_float, to_int
from app.services.audit import log
from app.web import templates

router = APIRouter()


def _project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.get("/projects", response_class=HTMLResponse)
def list_projects(
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    projects = list(
        db.scalars(select(Project).order_by(Project.updated_at.desc())).all()
    )
    return templates.TemplateResponse(
        request=request,
        name="projects/list.html",
        context={"request": request, "user": user, "projects": projects},
    )


@router.get("/projects/new", response_class=HTMLResponse)
def new_project(
    request: Request,
    user: User = Depends(require_user),
):
    return templates.TemplateResponse(
        request=request,
        name="projects/new.html",
        context={"request": request, "user": user},
    )


@router.post("/projects")
def create_project(
    request: Request,
    name: str = Form(...),
    code: str = Form(""),
    client_name: str = Form(""),
    client_rut: str = Form(""),
    connection_type: str = Form("netbilling"),
    annual_consumption_kwh: str = Form("0"),
    tariff_clp_kwh: str = Form("150"),
    discount_rate: str = Form("8"),
    analysis_years: str = Form("25"),
    opex_pct: str = Form("1"),
    energy_price_increment: str = Form("3"),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = Project(
        org_id=user.org_id,
        name=name.strip(),
        code=code.strip() or None,
        client_name=client_name.strip() or None,
        client_rut=client_rut.strip() or None,
        connection_type=connection_type,
        annual_consumption_kwh=to_float(annual_consumption_kwh),
        tariff_clp_kwh=to_float(tariff_clp_kwh, 150),
        discount_rate=percent(discount_rate, 8),
        analysis_years=to_int(analysis_years, 25),
        opex_pct=percent(opex_pct, 1),
        energy_price_increment=percent(energy_price_increment, 3),
    )
    db.add(project)
    db.flush()
    log(db, user, "project", project.id, "created", {"name": project.name})
    db.commit()
    return RedirectResponse(f"/projects/{project.id}", status_code=303)


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(
    project_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = _project(db, project_id)
    designs = list(
        db.scalars(
            select(Design)
            .where(Design.project_id == project.id)
            .order_by(Design.created_at.desc(), Design.id.desc())
        ).all()
    )
    documents = list(
        db.scalars(
            select(Document)
            .where(Document.project_id == project.id)
            .order_by(Document.created_at.desc())
        ).all()
    )
    panels = list(
        db.scalars(
            select(Equipment)
            .where(Equipment.category == "Panel", Equipment.active.is_(True))
            .order_by(Equipment.price_clp.asc())
        ).all()
    )
    inverters = list(
        db.scalars(
            select(Equipment)
            .where(Equipment.category == "Inversor", Equipment.active.is_(True))
            .order_by(Equipment.power_w.asc())
        ).all()
    )
    roofs = list(project.site.roofs) if project.site else []
    return templates.TemplateResponse(
        request=request,
        name="projects/detail.html",
        context={
            "request": request,
            "user": user,
            "project": project,
            "designs": designs,
            "documents": documents,
            "panels": panels,
            "inverters": inverters,
            "roofs": roofs,
            "latest_design": designs[0] if designs else None,
        },
    )


@router.post("/projects/{project_id}/edit")
def update_project(
    project_id: int,
    request: Request,
    name: str = Form(...),
    code: str = Form(""),
    client_name: str = Form(""),
    client_rut: str = Form(""),
    connection_type: str = Form("netbilling"),
    annual_consumption_kwh: str = Form("0"),
    tariff_clp_kwh: str = Form("150"),
    discount_rate: str = Form("8"),
    analysis_years: str = Form("25"),
    opex_pct: str = Form("1"),
    energy_price_increment: str = Form("3"),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = _project(db, project_id)
    project.name = name.strip()
    project.code = code.strip() or None
    project.client_name = client_name.strip() or None
    project.client_rut = client_rut.strip() or None
    project.connection_type = connection_type
    project.annual_consumption_kwh = to_float(annual_consumption_kwh)
    project.tariff_clp_kwh = to_float(tariff_clp_kwh, 150)
    project.discount_rate = percent(discount_rate, 8)
    project.analysis_years = to_int(analysis_years, 25)
    project.opex_pct = percent(opex_pct, 1)
    project.energy_price_increment = percent(energy_price_increment, 3)
    log(db, user, "project", project.id, "updated", {"name": project.name})
    db.commit()
    return RedirectResponse(f"/projects/{project.id}?notice=Proyecto+actualizado", status_code=303)


@router.get("/projects/{project_id}/site", response_class=HTMLResponse)
def site_page(
    project_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = _project(db, project_id)
    site = project.site
    roofs = list(site.roofs) if site else []
    roof = roofs[0] if roofs else None
    site_data = {
        "projectId": project.id,
        "roofId": roof.id if roof else None,
        "latitude": site.latitude if site else -33.45,
        "longitude": site.longitude if site else -70.67,
        "roofGeojson": json.loads(roof.geom_geojson) if roof else None,
        "obstacles": [
            {
                "id": obstacle.id,
                "name": obstacle.name,
                "heightM": obstacle.height_m,
                "kind": obstacle.kind,
                "geojson": json.loads(obstacle.geom_geojson),
            }
            for obstacle in (roof.obstacles if roof else [])
        ],
    }
    return templates.TemplateResponse(
        request=request,
        name="projects/site.html",
        context={
            "request": request,
            "user": user,
            "project": project,
            "site": site,
            "roofs": roofs,
            "roof": roof,
            "site_data": site_data,
        },
    )


@router.post("/projects/{project_id}/site")
def save_site(
    project_id: int,
    request: Request,
    address: str = Form(""),
    comuna: str = Form(""),
    region: str = Form(""),
    latitude: str = Form("-33.45"),
    longitude: str = Form("-70.67"),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = _project(db, project_id)
    site = project.site
    if site is None:
        site = Site(project_id=project.id)
        db.add(site)
        db.flush()
    site.address = address.strip()
    site.comuna = comuna.strip() or None
    site.region = region.strip() or None
    site.latitude = to_float(latitude, -33.45)
    site.longitude = to_float(longitude, -70.67)
    log(
        db,
        user,
        "site",
        site.id,
        "saved",
        {"address": site.address, "latitude": site.latitude, "longitude": site.longitude},
    )
    db.commit()
    return RedirectResponse(
        f"/projects/{project.id}/site?notice=Emplazamiento+guardado", status_code=303
    )


@router.get("/projects/{project_id}/documents", response_class=HTMLResponse)
def project_documents(
    project_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = _project(db, project_id)
    documents = list(
        db.scalars(
            select(Document)
            .where(Document.project_id == project.id)
            .order_by(Document.created_at.desc())
        ).all()
    )
    return templates.TemplateResponse(
        request=request,
        name="documents/list.html",
        context={
            "request": request,
            "user": user,
            "project": project,
            "documents": documents,
        },
    )
