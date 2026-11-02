from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import require_user
from app.db import get_db
from app.models import (
    Design,
    Document,
    Equipment,
    FinancialRun,
    Project,
    Roof,
    Simulation,
    User,
)
from app.routers.utils import to_float
from app.services.audit import log
from app.services.design import (
    latest_compliance,
    latest_financial,
    latest_simulation,
    recalculate_design,
)
from app.services.documents import render_documents
from app.services.finance import analyze, annual_savings
from app.services.pv import simulate_pv
from app.services.weather import get_weather
from app.web import templates

router = APIRouter()


def _design(db: Session, design_id: int) -> Design:
    design = db.get(Design, design_id)
    if design is None:
        raise HTTPException(status_code=404, detail="Diseño no encontrado")
    return design


@router.post("/projects/{project_id}/designs")
def create_design(
    project_id: int,
    request: Request,
    roof_id: int = Form(...),
    panel_id: int = Form(...),
    inverter_id: int = Form(...),
    tilt_deg: str = Form("20"),
    azimuth_deg: str = Form("180"),
    name: str = Form("Diseño FV"),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    roof = db.get(Roof, roof_id)
    panel = db.get(Equipment, panel_id)
    inverter = db.get(Equipment, inverter_id)
    if roof is None or roof.site is None or roof.site.project_id != project.id:
        raise HTTPException(status_code=400, detail="Techumbre no válida para este proyecto")
    if panel is None or panel.category != "Panel":
        raise HTTPException(status_code=400, detail="Panel no válido")
    if inverter is None or inverter.category != "Inversor":
        raise HTTPException(status_code=400, detail="Inversor no válido")

    design = Design(
        project_id=project.id,
        roof_id=roof.id,
        panel_id=panel.id,
        inverter_id=inverter.id,
        name=name.strip() or "Diseño FV",
        tilt_deg=to_float(tilt_deg, roof.tilt_deg),
        azimuth_deg=to_float(azimuth_deg, roof.azimuth_deg),
    )
    db.add(design)
    db.flush()
    recalculate_design(db, design, roof, panel, inverter)
    project.status = "diseñado"
    log(db, user, "design", design.id, "created", {"panel": panel.label, "inverter": inverter.label})
    db.commit()
    return RedirectResponse(f"/designs/{design.id}", status_code=303)


@router.get("/designs/{design_id}", response_class=HTMLResponse)
def design_detail(
    design_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    design = _design(db, design_id)
    simulation = latest_simulation(db, design)
    financial = latest_financial(db, design)
    compliance = latest_compliance(db, design)
    bom_items = list(design.bom_items)
    role_order = ["panel", "inversor", "estructura", "instalación", "contingencia"]
    bom_items.sort(key=lambda item: role_order.index(item.role) if item.role in role_order else 99)
    design_data = {
        "layout": json.loads(design.layout_geojson) if design.layout_geojson else None,
        "roof": json.loads(design.roof.geom_geojson) if design.roof else None,
        "latitude": design.roof.site.latitude if design.roof and design.roof.site else -33.45,
        "longitude": design.roof.site.longitude if design.roof and design.roof.site else -70.67,
    }
    return templates.TemplateResponse(
        request=request,
        name="designs/detail.html",
        context={
            "request": request,
            "user": user,
            "design": design,
            "project": design.project,
            "roof": design.roof,
            "site": design.roof.site if design.roof else None,
            "simulation": simulation,
            "financial": financial,
            "compliance": compliance,
            "bom_items": bom_items,
            "design_data": design_data,
            "capex": sum(item.total_clp for item in bom_items),
        },
    )


@router.post("/designs/{design_id}/layout")
def recalculate(
    design_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    design = _design(db, design_id)
    for simulation in list(design.simulations):
        db.delete(simulation)
    for run in list(design.financial_runs):
        db.delete(run)
    db.flush()
    recalculate_design(db, design, design.roof, design.panel, design.inverter)
    design.project.status = "diseñado"
    log(db, user, "design", design.id, "layout_recalculated", {"panels": design.panel_count})
    db.commit()
    return RedirectResponse(
        f"/designs/{design.id}?notice=Distribuci%C3%B3n+recalculada%3B+vuelve+a+simular",
        status_code=303,
    )


@router.post("/designs/{design_id}/simulate")
def simulate(
    design_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    design = _design(db, design_id)
    site = design.roof.site if design.roof else None
    if site is None:
        raise HTTPException(status_code=400, detail="El diseño no tiene emplazamiento")

    weather = get_weather(site.latitude, site.longitude)
    result = simulate_pv(
        weather=weather["dataframe"],
        latitude=site.latitude,
        longitude=site.longitude,
        tilt_deg=design.tilt_deg,
        azimuth_deg=design.azimuth_deg,
        panel_count=design.panel_count,
        panel_power_w=design.panel.power_w,
        inverter_ac_w=design.inverter.power_w,
        inverter_efficiency=design.inverter.efficiency or 0.97,
    )
    simulation = Simulation(
        design_id=design.id,
        status="ok" if not weather["warning"] else "respaldo",
        annual_kwh=result["annual_kwh"],
        specific_yield=result["specific_yield"],
        performance_ratio=result["performance_ratio"],
        weather_source=weather["source"],
        weather_year=weather["year"],
        result_json={
            "monthly": result["monthly"],
            "capacity_factor": result["capacity_factor"],
            "poa_kwh_m2": result["poa_kwh_m2"],
            "warning": weather["warning"],
        },
    )
    db.add(simulation)
    db.flush()
    recalculate_design(db, design, design.roof, design.panel, design.inverter)
    design.status = "simulado"
    design.project.status = "simulado"
    log(db, user, "design", design.id, "simulated", {"annual_kwh": result["annual_kwh"], "source": weather["source"]})
    db.commit()
    return RedirectResponse(
        f"/designs/{design.id}?notice=Simulaci%C3%B3n+completada", status_code=303
    )


@router.post("/designs/{design_id}/financial")
def financial_analysis(
    design_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    design = _design(db, design_id)
    simulation = latest_simulation(db, design)
    if simulation is None:
        return RedirectResponse(
            f"/designs/{design.id}?notice=Primero+debes+simular+la+producci%C3%B3n",
            status_code=303,
        )

    capex = sum(item.total_clp for item in design.bom_items)
    savings = annual_savings(
        annual_kwh=simulation.annual_kwh,
        annual_consumption_kwh=design.project.annual_consumption_kwh,
        tariff_clp_kwh=design.project.tariff_clp_kwh,
    )
    result = analyze(
        capex_clp=capex,
        annual_savings_clp=savings,
        annual_opex_clp=capex * design.project.opex_pct,
        annual_kwh=simulation.annual_kwh,
        years=design.project.analysis_years,
        discount_rate=design.project.discount_rate,
    )
    run = FinancialRun(design_id=design.id)
    db.add(run)
    run.capex_clp = result["capex_clp"]
    run.annual_savings_clp = result["annual_savings_clp"]
    run.lcoe_clp_kwh = result["lcoe_clp_kwh"] or 0
    run.npv_clp = result["npv_clp"]
    run.irr = result["irr"]
    run.payback_years = result["payback_years"]
    run.assumptions_json = {
        "annual_opex_clp": result["annual_opex_clp"],
        "years": result["years"],
        "discount_rate": result["discount_rate"],
        "tariff_clp_kwh": design.project.tariff_clp_kwh,
    }
    design.status = "evaluado"
    design.project.status = "evaluado"
    log(db, user, "design", design.id, "financial_calculated", {"capex": capex, "npv": result["npv_clp"]})
    db.commit()
    return RedirectResponse(
        f"/designs/{design.id}?notice=Evaluaci%C3%B3n+econ%C3%B3mica+calculada", status_code=303
    )


@router.post("/designs/{design_id}/compliance")
def compliance_check(
    design_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    design = _design(db, design_id)
    recalculate_design(db, design, design.roof, design.panel, design.inverter)
    log(db, user, "design", design.id, "compliance_checked")
    db.commit()
    return RedirectResponse(
        f"/designs/{design.id}?notice=Chequeos+actualizados", status_code=303
    )


@router.post("/designs/{design_id}/documents")
def generate_documents(
    design_id: int,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    design = _design(db, design_id)
    simulation = latest_simulation(db, design)
    financial = latest_financial(db, design)
    if simulation is None or financial is None:
        return RedirectResponse(
            f"/designs/{design.id}?notice=Completa+simulaci%C3%B3n+y+econom%C3%ADa+antes+de+generar+documentos",
            status_code=303,
        )

    compliance = [
        {"rule": check.rule, "status": check.status, "message": check.message}
        for check in latest_compliance(db, design)
    ]
    paths = render_documents(
        project=design.project,
        site=design.roof.site if design.roof else None,
        roof=design.roof,
        design=design,
        simulation=simulation,
        financial=financial,
        compliance=compliance,
        bom_items=list(design.bom_items),
    )
    version = (
        db.scalar(
            select(func.count(Document.id)).where(
                Document.project_id == design.project_id,
                Document.design_id == design.id,
                Document.kind == "memoria_calculo",
            )
        )
        or 0
    )
    document = Document(
        project_id=design.project_id,
        design_id=design.id,
        kind="memoria_calculo",
        version=int(version) + 1,
        docx_path=paths["docx_path"],
        pdf_path=paths["pdf_path"],
        toml_path=paths["toml_path"],
    )
    db.add(document)
    design.status = "documentado"
    design.project.status = "documentado"
    db.flush()
    log(db, user, "document", document.id, "generated", {"design_id": design.id})
    db.commit()
    return RedirectResponse(
        f"/projects/{design.project_id}/documents?notice=Documentos+generados",
        status_code=303,
    )
