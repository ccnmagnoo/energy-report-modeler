"""Cálculo de la cadena eléctrica FV para el canvas de selección."""

from __future__ import annotations

from math import ceil, floor


def _spec(equipment, key: str):
    return (equipment.specs or {}).get(key) if equipment else None


def _check(label: str, status: str, message: str) -> dict:
    return {"label": label, "status": status, "message": message}


def build_preview(
    roof,
    panel,
    inverter,
    panel_count: int | None = None,
    estimated: bool = False,
    has_battery: bool = False,
) -> dict:
    if roof is None or panel is None or inverter is None:
        return {"error": "Selecciona una techumbre, un panel y un inversor."}

    panel_area = (panel.width_mm / 1000) * (panel.height_mm / 1000)
    if panel_area <= 0:
        return {"error": "El panel no tiene dimensiones válidas en el catálogo."}

    if panel_count is None:
        panel_count = max(
            0,
            floor((roof.area_m2 or 0) * (roof.usable_factor or 0) / panel_area),
        )
        estimated = True
    panel_count = max(0, int(panel_count))

    dc_kw = panel_count * (panel.power_w or 0) / 1000
    ac_kw = (inverter.power_w or 0) / 1000
    dc_ac_ratio = (dc_kw / ac_kw) if ac_kw else None

    vmp = _spec(panel, "vmp")
    imp = _spec(panel, "imp")
    voc = _spec(panel, "voc")
    isc = _spec(panel, "isc")
    mppt_min = _spec(inverter, "mppt_min")
    mppt_max = _spec(inverter, "mppt_max")
    max_voltage = _spec(inverter, "max_voltage")
    max_input_current = _spec(inverter, "max_input_current")
    max_dc_w = _spec(inverter, "max_dc_w")

    modules_per_string = None
    strings = None
    string_voltage = None
    string_current = None
    if vmp and mppt_max:
        modules_per_string = max(1, floor(float(mppt_max) / float(vmp)))
        if panel_count:
            modules_per_string = min(modules_per_string, panel_count)
        if modules_per_string:
            strings = ceil(panel_count / modules_per_string) if panel_count else 0
            string_voltage = float(vmp) * modules_per_string
            if imp and strings:
                string_current = float(imp) * strings

    checks: list[dict] = []
    panel_data = all(value is not None for value in (vmp, imp, voc, isc))
    checks.append(
        _check(
            "Datos eléctricos del panel",
            "ok" if panel_data else "missing",
            "Vmp, Imp, Voc e Isc disponibles."
            if panel_data
            else "Completa Vmp, Imp, Voc e Isc en el catálogo.",
        )
    )
    inverter_data = all(
        value is not None
        for value in (mppt_min, mppt_max, max_voltage, max_input_current, max_dc_w)
    )
    checks.append(
        _check(
            "Datos MPPT del inversor",
            "ok" if inverter_data else "missing",
            "Rango MPPT, tensión y corriente disponibles."
            if inverter_data
            else "Completa rango MPPT, tensión máxima y corriente máxima en el catálogo.",
        )
    )

    if panel_count <= 0:
        checks.append(
            _check("Cantidad de módulos", "warning", "La techumbre no permite estimar módulos.")
        )
    else:
        checks.append(
            _check("Cantidad de módulos", "ok", f"{panel_count} módulos considerados.")
        )

    if string_voltage is not None and mppt_min is not None and mppt_max is not None:
        if float(mppt_min) <= string_voltage <= float(mppt_max):
            checks.append(
                _check(
                    "Tensión de string",
                    "ok",
                    f"{string_voltage:.1f} V dentro del rango MPPT {mppt_min}–{mppt_max} V.",
                )
            )
        else:
            checks.append(
                _check(
                    "Tensión de string",
                    "warning",
                    f"{string_voltage:.1f} V fuera del rango MPPT {mppt_min}–{mppt_max} V.",
                )
            )
    else:
        checks.append(
            _check("Tensión de string", "missing", "Faltan Vmp o rango MPPT.")
        )

    if string_voltage is not None and max_voltage is not None and string_voltage > float(max_voltage):
        checks.append(
            _check(
                "Tensión máxima DC",
                "error",
                f"{string_voltage:.1f} V supera la tensión máxima {max_voltage} V.",
            )
        )

    if string_current is not None and max_input_current is not None:
        if string_current <= float(max_input_current):
            checks.append(
                _check(
                    "Corriente de entrada",
                    "ok",
                    f"{string_current:.1f} A ≤ {max_input_current} A.",
                )
            )
        else:
            checks.append(
                _check(
                    "Corriente de entrada",
                    "warning",
                    f"{string_current:.1f} A supera la corriente máxima {max_input_current} A.",
                )
            )
    else:
        checks.append(
            _check("Corriente de entrada", "missing", "Faltan Imp o corriente máxima.")
        )

    if max_dc_w is not None:
        dc_w = dc_kw * 1000
        if dc_w <= float(max_dc_w):
            checks.append(
                _check("Potencia DC del inversor", "ok", f"{dc_w:.0f} W ≤ {max_dc_w} W.")
            )
        else:
            checks.append(
                _check(
                    "Potencia DC del inversor",
                    "warning",
                    f"{dc_w:.0f} W supera el máximo {max_dc_w} W.",
                )
            )
    else:
        checks.append(
            _check("Potencia DC del inversor", "missing", "Falta la potencia máxima DC.")
        )

    if dc_ac_ratio is not None:
        if 0.8 <= dc_ac_ratio <= 1.3:
            checks.append(
                _check("Relación DC/AC", "ok", f"Relación DC/AC = {dc_ac_ratio:.2f}.")
            )
        else:
            checks.append(
                _check(
                    "Relación DC/AC",
                    "warning",
                    f"Relación DC/AC = {dc_ac_ratio:.2f}; revisar dimensionamiento.",
                )
            )
    else:
        checks.append(
            _check("Relación DC/AC", "missing", "Falta la potencia AC del inversor.")
        )

    return {
        "panel": panel,
        "inverter": inverter,
        "panel_label": panel.label,
        "inverter_label": inverter.label,
        "panel_count": panel_count,
        "estimated": estimated,
        "dc_kw": round(dc_kw, 2),
        "ac_kw": round(ac_kw, 2),
        "dc_ac_ratio": round(dc_ac_ratio, 2) if dc_ac_ratio is not None else None,
        "modules_per_string": modules_per_string,
        "strings": strings,
        "string_voltage": round(string_voltage, 1) if string_voltage is not None else None,
        "string_current": round(string_current, 1) if string_current is not None else None,
        "roof_area_m2": round(float(roof.area_m2 or 0), 1),
        "panel_area_m2": round(panel_area, 2),
        "has_battery": has_battery,
        "checks": checks,
    }
