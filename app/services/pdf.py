"""Conversión DOCX a PDF con Word y respaldo ReportLab."""

from __future__ import annotations

import os
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document as DocxDocument
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors


def _fallback_pdf(docx_path: Path, pdf_path: Path) -> bool:
    """Genera un PDF legible aunque Word no esté disponible."""

    source = DocxDocument(str(docx_path))
    styles = getSampleStyleSheet()
    story = []
    for paragraph in source.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        style = styles["Heading2"] if paragraph.style.name.startswith("Heading") else styles["BodyText"]
        story.append(Paragraph(escape(text), style))
        story.append(Spacer(1, 4))

    for table in source.tables:
        data = [
            [Paragraph(escape(cell.text.strip()), styles["BodyText"]) for cell in row.cells]
            for row in table.rows
        ]
        if data:
            report_table = Table(data, repeatRows=1, hAlign="LEFT")
            report_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c9d4e2")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2a44")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.append(report_table)
            story.append(Spacer(1, 8))

    if not story:
        story = [Paragraph("Documento sin contenido", styles["Title"])]

    pdf = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    pdf.build(story)
    return pdf_path.exists()


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> bool:
    """Convierte DOCX a PDF.

    ``FV_PDF_CONVERTER`` acepta ``auto`` (Word y respaldo), ``word`` (solo Word),
    ``reportlab`` (respaldo) o ``none`` (no generar PDF).
    """

    mode = os.getenv("FV_PDF_CONVERTER", "auto").lower()
    if mode == "none":
        return False

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if mode in {"auto", "word"}:
        try:
            from docx2pdf import convert

            convert(str(docx_path), str(pdf_path))
            if pdf_path.exists():
                return True
        except Exception:
            if mode == "word":
                return False

    if mode in {"auto", "reportlab"}:
        try:
            return _fallback_pdf(docx_path, pdf_path)
        except Exception:
            return False
    return False
