"""Chequeos técnicos y normativos básicos para el MVP.

No reemplazan la revisión de un instalador eléctrico SEC ni la memoria firmada
por un profesional competente. Son advertencias tempranas de diseño.
"""

from __future__ import annotations

from app.models import Design, Equipment, Roof, Simulation


def run_checks(
    design: Design,
    roof: Roof,
    inverter: Equipment,
    simulation: Simulation | None = None,
) -> list[dict]:
    max_dc_w = float(inverter.specs.get("max_dc_w", inverter.power_w * 1.3))
    dc_ac_ratio = design.dc_kw / design.ac_kw if design.ac_kw else None

    checks: list[dict] = []

    def add(rule: str, status: str, message: str) -> None:
        checks.append({"rule": rule, "status": status, "message": message})

    if design.panel_count > 0:
        add("Distribución de módulos", "ok", f"{design.panel_count} módulos distribuidos.")
    else:
        add("Distribución de módulos", "error", "No se pudo distribuir ningún módulo en la techumbre.")

    if dc_ac_ratio is None:
        add("Relación DC/AC", "error", "No se pudo calcular la relación DC/AC.")
    elif 0.8 <= dc_ac_ratio <= 1.3:
        add("Relación DC/AC", "ok", f"Relación DC/AC = {dc_ac_ratio:.2f}.")
    else:
        add(
            "Relación DC/AC",
            "warning",
            f"Relación DC/AC = {dc_ac_ratio:.2f}; revisar el dimensionamiento del inversor.",
        )

    dc_w = design.dc_kw * 1000
    if dc_w <= max_dc_w:
        add("Límite DC del inversor", "ok", f"DC {dc_w:.0f} W ≤ máximo {max_dc_w:.0f} W.")
    else:
        add(
            "Límite DC del inversor",
            "error",
            f"DC {dc_w:.0f} W supera el máximo del inversor ({max_dc_w:.0f} W).",
        )

    if design.occupancy <= 0.85:
        add("Ocupación de techumbre", "ok", f"Ocupación {design.occupancy * 100:.1f} %.")
    else:
        add(
            "Ocupación de techumbre",
            "warning",
            f"Ocupación {design.occupancy * 100:.1f} %; verificar circulación y mantenciones.",
        )

    if 0 <= design.tilt_deg <= 60:
        add("Inclinación", "ok", f"Inclinación {design.tilt_deg:.1f}°.")
    else:
        add("Inclinación", "warning", f"Inclinación {design.tilt_deg:.1f}° fuera del rango típico 0–60°.")

    if 0 <= design.azimuth_deg <= 360:
        add("Azimut", "ok", f"Azimut {design.azimuth_deg:.1f}°.")
    else:
        add("Azimut", "warning", f"Azimut {design.azimuth_deg:.1f}° fuera de 0–360°.")

    if roof.area_m2 > 0:
        add("Superficie de techumbre", "ok", f"{roof.area_m2:.1f} m² registrados.")
    else:
        add("Superficie de techumbre", "error", "La techumbre no tiene superficie calculada.")

    if simulation and simulation.annual_kwh > 0:
        add(
            "Producción estimada",
            "ok",
            f"{simulation.annual_kwh:,.0f} kWh/año con {simulation.weather_source}.".replace(",", "."),
        )
    else:
        add("Producción estimada", "warning", "Aún no existe una simulación de producción.")

    add(
        "Revisión profesional",
        "warning",
        "Los documentos son borradores y requieren revisión y firma de profesional competente.",
    )
    return checks
