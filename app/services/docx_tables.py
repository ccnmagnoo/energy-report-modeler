"""Inserción de tablas nativas de Word en los placeholders table_*."""

from __future__ import annotations

from dataclasses import dataclass

from docx.document import Document as DocxDocument

from app.services.docx_templates import iter_all_paragraphs


@dataclass
class TableData:
    headers: list[str]
    rows: list[list[str]]


def _fill_cell(cell, value: str, bold: bool = False) -> None:
    cell.text = str(value)
    if bold:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True


def replace_tables(doc: DocxDocument, tables: dict[str, TableData]) -> None:
    """Reemplaza tokens por tablas Word reales.

    Los tokens se insertan como texto durante el render de docxtpl. Luego se
    busca el párrafo que los contiene y se intercambia por una tabla.
    """

    for token, data in tables.items():
        paragraph = next(
            (item for item in iter_all_paragraphs(doc) if token in item.text),
            None,
        )
        if paragraph is None:
            continue

        table = doc.add_table(rows=1 + len(data.rows), cols=len(data.headers))
        table.style = "Table Grid"
        table.autofit = True

        for index, header in enumerate(data.headers):
            _fill_cell(table.rows[0].cells[index], header, bold=True)
        for row_index, row in enumerate(data.rows, start=1):
            for column_index, value in enumerate(row):
                if column_index < len(data.headers):
                    _fill_cell(table.rows[row_index].cells[column_index], value)

        paragraph._p.addnext(table._tbl)
        paragraph._p.getparent().remove(paragraph._p)
