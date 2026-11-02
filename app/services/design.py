"""Orquestación del diseño: layout, BOM y chequeos."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BOMItem, ComplianceCheck, Design, Equipment, FinancialRun, Roof, Simulation
from app.services.compliance import run_checks
from app.services.layout import generate_layout


def latest_simulation(db: Session, design: Design) -> Simulation | None:
    return db.scalar(
        select(Simulation)
        .where(Simulation.design_id == design.id)
        .order_by(Simulation.created_at.desc(), Simulation.id.desc())
        .limit(1)
    )


def latest_financial(db: Session, design: Design) -> FinancialRun | None:
    return db.scalar(
        select(FinancialRun)
        .where(FinancialRun.design_id == design.id)
        .order_by(FinancialRun.created_at.desc(), FinancialRun.id.desc())
        .limit(1)
    )


def latest_compliance(db: Session, design: Design) -> list[ComplianceCheck]:
    return list(
        db.scalars(
            select(ComplianceCheck)
            .where(ComplianceCheck.design_id == design.id)
            .order_by(ComplianceCheck.id.asc())
        ).all()
    )


def _structure(db: Session) -> Equipment | None:
    return db.scalar(
        select(Equipment)
        .where(Equipment.category == "Estructura", Equipment.active.is_(True))
        .order_by(Equipment.price_clp.asc())
        .limit(1)
    )


def _replace_bom(db: Session, design: Design, panel: Equipment, inverter: Equipment) -> None:
    for item in list(design.bom_items):
        db.delete(item)
    db.flush()

    structure = _structure(db)
    equipment_subtotal = (
        design.panel_count * panel.price_clp
        + inverter.price_clp
        + (design.panel_count * structure.price_clp if structure else 0)
    )
    installation = equipment_subtotal * 0.15
    contingency = (equipment_subtotal + installation) * 0.05

    design.bom_items = [
        BOMItem(
            design_id=design.id,
            equipment_id=panel.id,
            role="panel",
            description=panel.label,
            quantity=design.panel_count,
            unit_price_clp=panel.price_clp,
        ),
        BOMItem(
            design_id=design.id,
            equipment_id=inverter.id,
            role="inversor",
            description=inverter.label,
            quantity=1,
            unit_price_clp=inverter.price_clp,
        ),
        BOMItem(
            design_id=design.id,
            equipment_id=structure.id if structure else None,
            role="estructura",
            description=structure.label if structure else "Estructura de montaje",
            quantity=design.panel_count,
            unit_price_clp=structure.price_clp if structure else 0,
        ),
        BOMItem(
            design_id=design.id,
            role="instalación",
            description="Instalación, certificación y gestión SEC (estimada)",
            quantity=1,
            unit_price_clp=round(installation, 2),
        ),
        BOMItem(
            design_id=design.id,
            role="contingencia",
            description="Contingencia de proyecto (5 %)",
            quantity=1,
            unit_price_clp=round(contingency, 2),
        ),
    ]
    db.flush()


def _replace_compliance(db: Session, design: Design, roof: Roof, inverter: Equipment) -> None:
    for check in list(design.compliance_checks):
        db.delete(check)
    db.flush()
    simulation = latest_simulation(db, design)
    for result in run_checks(design, roof, inverter, simulation):
        db.add(
            ComplianceCheck(
                design_id=design.id,
                rule=result["rule"],
                status=result["status"],
                message=result["message"],
            )
        )
    db.flush()


def recalculate_design(
    db: Session,
    design: Design,
    roof: Roof,
    panel: Equipment,
    inverter: Equipment,
) -> dict:
    panel_width = max(0.5, panel.width_mm / 1000)
    panel_height = max(0.5, panel.height_mm / 1000)
    layout = generate_layout(
        roof_geojson=roof.geom_geojson,
        panel_width_m=panel_width,
        panel_height_m=panel_height,
        tilt_deg=design.tilt_deg,
        usable_factor=roof.usable_factor,
        latitude=roof.site.latitude if roof.site else -33.45,
        longitude=roof.site.longitude if roof.site else -70.67,
    )

    design.panel_count = layout["count"]
    design.dc_kw = round(layout["count"] * panel.power_w / 1000, 3)
    design.ac_kw = round(inverter.power_w / 1000, 3)
    design.occupancy = layout["occupancy"]
    design.layout_geojson = json.dumps(layout["geojson"])
    design.status = "diseñado"

    _replace_bom(db, design, panel, inverter)
    _replace_compliance(db, design, roof, inverter)
    db.flush()
    return layout
