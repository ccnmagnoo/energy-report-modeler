"""Carga y saneamiento de las plantillas Word existentes.

Las plantillas fueron editadas en Word y contienen comillas tipográficas dentro
de expresiones Jinja, además de etiquetas repartidas entre runs. Este módulo
crea una copia saneada en caché antes de entregarla a docxtpl.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docxtpl import DocxTemplate, RichText

from app.config import DATA_DIR

TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"
SANITIZED_DIR = DATA_DIR / "cache" / "templates"
SANITIZER_VERSION = "2"

_SMART_QUOTES = str.maketrans(
    {
        "\u2018": "'",  # ‘
        "\u2019": "'",  # ’
        "\u201c": "'",  # “
        "\u201d": "'",  # ”
    }
)
_JINJA_TAG = re.compile(r"(\{\{.*?\}\}|\{%.*?%\})", re.S)


def iter_paragraphs(container) -> Iterator[Paragraph]:
    for paragraph in container.paragraphs:
        yield paragraph
    for table in container.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from iter_paragraphs(cell)


def iter_all_paragraphs(doc: Document) -> Iterator[Paragraph]:
    yield from iter_paragraphs(doc)
    for section in doc.sections:
        for part in (section.header, section.footer):
            yield from iter_paragraphs(part)


def _sanitize_paragraph(paragraph: Paragraph) -> None:
    if not paragraph.runs:
        return
    text = "".join(run.text for run in paragraph.runs)
    if "{{" not in text and "{%" not in text:
        return

    normalized = _JINJA_TAG.sub(
        lambda match: match.group(1).translate(_SMART_QUOTES), text
    )
    first = paragraph.runs[0]
    for run in paragraph.runs[1:]:
        run._r.getparent().remove(run._r)
    first.text = normalized


def prepare_template(source_name: str) -> Path:
    """Devuelve una copia DOCX con las expresiones Jinja normalizadas."""

    source = TEMPLATE_DIR / source_name
    if not source.exists():
        raise FileNotFoundError(f"No existe la plantilla {source}")
    target = SANITIZED_DIR / f"{source.stem}_sanitized_v{SANITIZER_VERSION}.docx"
    SANITIZED_DIR.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
        return target

    doc = Document(str(source))
    for paragraph in iter_all_paragraphs(doc):
        _sanitize_paragraph(paragraph)
    doc.save(target)
    return target


def _gmaps_richtext(template: DocxTemplate, latitude: float, longitude: float) -> RichText:
    url = (
        f"https://www.google.com/maps/@{latitude},{longitude},"
        "200m/data=!3m1!1e3?entry=ttu"
    )
    rich = RichText()
    rich.add(
        "ver maps",
        url_id=template.build_url_id(url),
        bold=True,
        underline=True,
    )
    return rich


def _replace_pictures(template: DocxTemplate, pictures: dict[str, Path]) -> None:
    for name, path in pictures.items():
        if path and Path(path).exists():
            try:
                template.replace_pic(name, str(path))
            except Exception:
                # Una imagen faltante no debe impedir la generación del documento.
                continue


def render_memory(
    context: dict,
    tables: dict,
    pictures: dict[str, Path],
    output_path: Path,
    latitude: float,
    longitude: float,
) -> Path:
    """Renderiza la memoria de cálculo sobre memory_template.docx."""

    template = DocxTemplate(str(prepare_template("memory_template.docx")))
    context = dict(context)
    context["gmaps"] = _gmaps_richtext(template, latitude, longitude)
    template.render(context)

    from app.services.docx_tables import replace_tables

    replace_tables(template.docx, tables)
    _replace_pictures(template, pictures)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template.save(output_path)
    return output_path


def render_bidding(
    context: dict,
    output_path: Path,
    latitude: float,
    longitude: float,
) -> Path:
    """Renderiza el pliego de licitación sobre bidding_template.docx."""

    template = DocxTemplate(str(prepare_template("bidding_template.docx")))
    context = dict(context)
    context["gmaps"] = _gmaps_richtext(template, latitude, longitude)
    template.render(context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template.save(output_path)
    return output_path
