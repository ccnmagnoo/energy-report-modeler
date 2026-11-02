"""Parseo tolerante de formularios es-CL."""

from __future__ import annotations


def to_float(value: str | float | int | None, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(" ", "")
    if not text:
        return default
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return default


def to_int(value: str | int | None, default: int = 0) -> int:
    try:
        return int(to_float(value, default))
    except (TypeError, ValueError):
        return default


def percent(value: str | float | None, default: float = 0.0) -> float:
    """Convierte un porcentaje escrito como 8 a 0.08."""
    return to_float(value, default * 100) / 100
