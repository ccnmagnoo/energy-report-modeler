"""Generación de documentos: memoria de cálculo y pliego de licitación."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import tomli_w

from app.config import DOCUMENTS_DIR
from app.services.docx_context import build_context
from app.services.docx_plots import generate_plots
from app.services.docx_templates import render_bidding, render_memory
from app.services.pdf import convert_docx_to_pdf


def _serialize(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


def _toml_safe(value: Any) -> Any:
    value = _serialize(value)
    if isinstance(value, dict):
        return {
            str(key): _toml_safe(item)
            for key, item in value.items()
            if item is not None
        }
    if isinstance(value, list):
        return [_toml_safe(item) for item in value if item is not None]
    return value


def build_snapshot(
    project,
    site,
    roof,
    design,
    simulation,
    financial,
    compliance: list[dict],
    bom_items: list,
    document_type: str = "memoria_calculo",
) -> dict:
    return _toml_safe(
        {
            "app": "Modelador de Reportes FV",
            "version": "0.1.0",
            "document_type": document_type,
            "generated_at": datetime.now(),
            "project": {
                "id": project.id,
                "name": project.name,
                "code": project.code,
                "client_name": project.client_name,
                "client_rut": project.client_rut,
                "connection_type": project.connection_type,
                "annual_consumption_kwh": project.annual_consumption_kwh,
                "tariff_clp_kwh": project.tariff_clp_kwh,
                "discount_rate": project.discount_rate,
                "analysis_years": project.analysis_years,
            },
            "site": {
                "address": site.address if site else None,
                "comuna": site.comuna if site else None,
                "region": site.region if site else None,
                "latitude": site.latitude if site else None,
                "longitude": site.longitude if site else None,
            },
            "roof": {
                "name": roof.name if roof else None,
                "area_m2": roof.area_m2 if roof else None,
                "tilt_deg": roof.tilt_deg if roof else None,
                "azimuth_deg": roof.azimuth_deg if roof else None,
                "material": roof.material if roof else None,
            },
            "design": {
                "id": design.id,
                "name": design.name,
                "panel_count": design.panel_count,
                "dc_kw": design.dc_kw,
                "ac_kw": design.ac_kw,
                "occupancy": design.occupancy,
                "tilt_deg": design.tilt_deg,
                "azimuth_deg": design.azimuth_deg,
                "panel": design.panel.label if design.panel else None,
                "inverter": design.inverter.label if design.inverter else None,
            },
            "simulation": {
                "annual_kwh": simulation.annual_kwh if simulation else None,
                "specific_yield": simulation.specific_yield if simulation else None,
                "performance_ratio": simulation.performance_ratio if simulation else None,
                "weather_source": simulation.weather_source if simulation else None,
                "weather_year": simulation.weather_year if simulation else None,
                "monthly": simulation.result_json.get("monthly", []) if simulation else [],
            },
            "financial": {
                "capex_clp": financial.capex_clp if financial else None,
                "annual_savings_clp": financial.annual_savings_clp if financial else None,
                "lcoe_clp_kwh": financial.lcoe_clp_kwh if financial else None,
                "npv_clp": financial.npv_clp if financial else None,
                "irr": financial.irr if financial else None,
                "payback_years": financial.payback_years if financial else None,
            },
            "compliance": compliance,
            "bom": [
                {
                    "role": item.role,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price_clp": item.unit_price_clp,
                    "total_clp": item.total_clp,
                }
                for item in bom_items
            ],
        }
    )


def generate_document(
    project,
    site,
    roof,
    design,
    simulation,
    financial,
    compliance: list[dict],
    bom_items: list,
    kind: str = "memoria_calculo",
    version: int = 1,
) -> dict:
    """Genera un documento DOCX/PDF/TOML a partir del modelo de datos."""

    if kind not in {"memoria_calculo", "pliego_licitacion"}:
        raise ValueError(f"Tipo de documento no soportado: {kind}")

    folder = (
        DOCUMENTS_DIR
        / str(project.id)
        / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        / kind
    )
    folder.mkdir(parents=True, exist_ok=True)

    context, tables = build_context(
        project=project,
        site=site,
        roof=roof,
        design=design,
        simulation=simulation,
        financial=financial,
        bom_items=bom_items,
        version=version,
    )

    latitude = site.latitude if site else -33.45
    longitude = site.longitude if site else -70.67

    if kind == "memoria_calculo":
        pictures = generate_plots(
            project=project,
            site=site,
            design=design,
            simulation=simulation,
            financial=financial,
            bom_items=bom_items,
            output_dir=folder / "figures",
        )
        docx_path = render_memory(
            context=context,
            tables=tables,
            pictures=pictures,
            output_path=folder / "memoria_calculo.docx",
            latitude=latitude,
            longitude=longitude,
        )
    else:
        docx_path = render_bidding(
            context=context,
            output_path=folder / "pliego_licitacion.docx",
            latitude=latitude,
            longitude=longitude,
        )

    pdf_path = folder / f"{kind}.pdf"
    pdf_ok = convert_docx_to_pdf(docx_path, pdf_path)

    snapshot = build_snapshot(
        project=project,
        site=site,
        roof=roof,
        design=design,
        simulation=simulation,
        financial=financial,
        compliance=compliance,
        bom_items=bom_items,
        document_type=kind,
    )
    toml_path = folder / f"{kind}.toml"
    toml_path.write_text(tomli_w.dumps(snapshot), encoding="utf-8")

    return {
        "docx_path": str(docx_path),
        "pdf_path": str(pdf_path) if pdf_ok else None,
        "toml_path": str(toml_path),
        "snapshot": snapshot,
    }
