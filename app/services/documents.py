"""Generación de memoria de cálculo en DOCX, PDF y snapshot TOML."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import tomli_w
from docx import Document as DocxDocument
from docx.shared import Cm, Pt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import DOCUMENTS_DIR


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
) -> dict:
    return _toml_safe(
        {
            "app": "Modelador de Reportes FV",
            "version": "0.1.0",
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
                "name": roof.name,
                "area_m2": roof.area_m2,
                "tilt_deg": roof.tilt_deg,
                "azimuth_deg": roof.azimuth_deg,
                "material": roof.material,
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


def _docx_table(doc, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cells[index].text = str(value)


def _money(value: float | None) -> str:
    if value is None:
        return "—"
    return f"CLP $ {value:,.0f}".replace(",", ".")


def _number(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_documents(
    project,
    site,
    roof,
    design,
    simulation,
    financial,
    compliance: list[dict],
    bom_items: list,
) -> dict:
    folder = DOCUMENTS_DIR / str(project.id) / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    folder.mkdir(parents=True, exist_ok=True)
    docx_path = folder / "memoria_calculo.docx"
    pdf_path = folder / "memoria_calculo.pdf"
    toml_path = folder / "resultados.toml"

    snapshot = build_snapshot(
        project, site, roof, design, simulation, financial, compliance, bom_items
    )

    # DOCX
    doc = DocxDocument()
    doc.core_properties.title = f"Memoria de cálculo - {project.name}"
    doc.core_properties.author = "Modelador de Reportes FV"
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)

    title = doc.add_heading("Modelador de Reportes FV", 0)
    title.alignment = 1
    subtitle = doc.add_paragraph("Memoria de cálculo y evaluación económica")
    subtitle.runs[0].bold = True
    subtitle.runs[0].font.size = Pt(13)
    subtitle.alignment = 1

    doc.add_heading("1. Identificación del proyecto", level=1)
    _docx_table(
        doc,
        ["Campo", "Valor"],
        [
            ["Proyecto", project.name],
            ["Código", project.code or "—"],
            ["Cliente", project.client_name or "—"],
            ["RUT", project.client_rut or "—"],
            ["Tipo de conexión", project.connection_type],
            ["Dirección", site.address if site else "—"],
            ["Comuna / Región", f"{site.comuna or '—'} / {site.region or '—'}" if site else "—"],
            ["Coordenadas", f"{site.latitude:.6f}, {site.longitude:.6f}" if site else "—"],
        ],
    )

    doc.add_heading("2. Techumbre y diseño fotovoltaico", level=1)
    _docx_table(
        doc,
        ["Parámetro", "Valor"],
        [
            ["Techumbre", roof.name],
            ["Superficie", f"{_number(roof.area_m2, 1)} m²"],
            ["Inclinación", f"{_number(design.tilt_deg, 1)}°"],
            ["Azimut", f"{_number(design.azimuth_deg, 1)}°"],
            ["Módulo", design.panel.label if design.panel else "—"],
            ["Inversor", design.inverter.label if design.inverter else "—"],
            ["Cantidad de módulos", str(design.panel_count)],
            ["Potencia DC", f"{_number(design.dc_kw, 2)} kWp"],
            ["Potencia AC", f"{_number(design.ac_kw, 2)} kW"],
            ["Ocupación", f"{_number(design.occupancy * 100, 1)} %"],
        ],
    )

    doc.add_heading("3. Producción estimada", level=1)
    if simulation:
        _docx_table(
            doc,
            ["Indicador", "Valor"],
            [
                ["Energía anual", f"{_number(simulation.annual_kwh, 0)} kWh/año"],
                ["Rendimiento específico", f"{_number(simulation.specific_yield, 0)} kWh/kWp"],
                ["Performance ratio", f"{_number(simulation.performance_ratio * 100, 1)} %"],
                ["Fuente climática", f"{simulation.weather_source} ({simulation.weather_year})"],
            ],
        )
    else:
        doc.add_paragraph("No existe simulación de producción registrada.")

    doc.add_heading("4. Evaluación económica", level=1)
    if financial:
        _docx_table(
            doc,
            ["Indicador", "Valor"],
            [
                ["CAPEX", _money(financial.capex_clp)],
                ["Ahorro anual", _money(financial.annual_savings_clp)],
                ["VAN", _money(financial.npv_clp)],
                ["TIR", f"{_number((financial.irr or 0) * 100, 2)} %"],
                ["Payback", f"{_number(financial.payback_years, 2)} años"],
                ["LCOE", f"CLP $ {_number(financial.lcoe_clp_kwh, 0)}/kWh"],
            ],
        )
    else:
        doc.add_paragraph("No existe evaluación económica registrada.")

    doc.add_heading("5. Listado de equipos", level=1)
    _docx_table(
        doc,
        ["Rol", "Descripción", "Cantidad", "Unitario", "Total"],
        [
            [
                item.role,
                item.description,
                _number(item.quantity, 0),
                _money(item.unit_price_clp),
                _money(item.total_clp),
            ]
            for item in bom_items
        ],
    )

    doc.add_heading("6. Cumplimiento y advertencias", level=1)
    _docx_table(
        doc,
        ["Regla", "Estado", "Mensaje"],
        [[item["rule"], item["status"], item["message"]] for item in compliance],
    )
    doc.add_paragraph(
        "Este documento es un borrador técnico generado automáticamente. "
        "Debe ser revisado y firmado por un profesional competente antes de "
        "presentarlo a la SEC, a una distribuidora o a un proceso de licitación."
    )
    doc.save(docx_path)

    # PDF
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Modelador de Reportes FV", styles["Title"]),
        Paragraph("Memoria de cálculo y evaluación económica", styles["Heading2"]),
        Spacer(1, 8),
    ]

    def add_pdf_table(headers: list[str], rows: list[list[str]]) -> None:
        data = [[Paragraph(f"<b>{escape(str(value))}</b>", styles["BodyText"]) for value in headers]]
        data += [
            [Paragraph(escape(str(value)), styles["BodyText"]) for value in row]
            for row in rows
        ]
        table = Table(data, repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2a44")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c9d4e2")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fb")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 8))

    story.append(Paragraph("1. Identificación del proyecto", styles["Heading2"]))
    add_pdf_table(
        ["Campo", "Valor"],
        [
            ["Proyecto", project.name],
            ["Cliente", project.client_name or "—"],
            ["Dirección", site.address if site else "—"],
            ["Comuna", site.comuna if site else "—"],
            ["Coordenadas", f"{site.latitude:.6f}, {site.longitude:.6f}" if site else "—"],
        ],
    )
    story.append(Paragraph("2. Diseño fotovoltaico", styles["Heading2"]))
    add_pdf_table(
        ["Parámetro", "Valor"],
        [
            ["Superficie", f"{_number(roof.area_m2, 1)} m²"],
            ["Módulos", f"{design.panel_count} x {design.panel.label if design.panel else '—'}"],
            ["Potencia DC", f"{_number(design.dc_kw, 2)} kWp"],
            ["Potencia AC", f"{_number(design.ac_kw, 2)} kW"],
            ["Producción anual", f"{_number(simulation.annual_kwh, 0)} kWh" if simulation else "—"],
            ["CAPEX", _money(financial.capex_clp) if financial else "—"],
            ["VAN", _money(financial.npv_clp) if financial else "—"],
            ["TIR", f"{_number((financial.irr or 0) * 100, 2)} %" if financial else "—"],
        ],
    )
    story.append(Paragraph("3. Cumplimiento", styles["Heading2"]))
    add_pdf_table(
        ["Regla", "Estado", "Mensaje"],
        [[item["rule"], item["status"], item["message"]] for item in compliance],
    )
    story.append(
        Paragraph(
            "Documento borrador generado automáticamente. Requiere revisión y firma "
            "de profesional competente.",
            styles["Italic"],
        )
    )
    pdf = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
        title=f"Memoria de cálculo - {project.name}",
    )
    pdf.build(story)

    toml_path.write_text(tomli_w.dumps(snapshot), encoding="utf-8")

    return {
        "docx_path": str(docx_path),
        "pdf_path": str(pdf_path),
        "toml_path": str(toml_path),
        "snapshot": snapshot,
    }
