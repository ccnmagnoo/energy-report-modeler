"""Utilidades de plantillas y formato es-CL."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def clp(value: float | int | None) -> str:
    if value is None:
        return "—"
    return f"${value:,.0f}".replace(",", ".")


def number(value: float | int | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value * 100:,.{decimals}f} %".replace(",", "X").replace(".", ",").replace("X", ".")


def date_cl(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%d-%m-%Y %H:%M")


templates.env.filters["clp"] = clp
templates.env.filters["num"] = number
templates.env.filters["pct"] = pct
templates.env.filters["date_cl"] = date_cl
