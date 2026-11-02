"""Modelo eléctrico simplificado de producción fotovoltaica."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pvlib


def simulate_pv(
    weather: pd.DataFrame,
    latitude: float,
    longitude: float,
    tilt_deg: float,
    azimuth_deg: float,
    panel_count: int,
    panel_power_w: float,
    inverter_ac_w: float,
    inverter_efficiency: float = 0.97,
    system_losses: float = 0.14,
    temperature_coefficient: float = -0.0035,
) -> dict:
    """Calcula producción horaria, mensual y anual.

    Se usa pvlib para la posición solar y la irradiancia en el plano de los
    módulos. El modelo de potencia es deliberadamente conservador y trazable:
    irradiancia POA, temperatura de célula, coeficiente de temperatura, pérdidas
    globales, límite de inversor y eficiencia de conversión.
    """

    if weather.empty:
        raise ValueError("No hay datos climáticos para simular")

    if panel_count <= 0 or panel_power_w <= 0:
        raise ValueError("La cantidad y potencia de paneles deben ser positivas")

    times = pd.DatetimeIndex(weather.index)
    if times.tz is None:
        times = times.tz_localize("Etc/GMT+4")
    else:
        times = times.tz_convert("Etc/GMT+4")

    location = pvlib.location.Location(latitude, longitude, tz="Etc/GMT+4")
    solar_position = location.get_solarposition(times)

    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt_deg,
        surface_azimuth=azimuth_deg,
        solar_zenith=solar_position["apparent_zenith"],
        solar_azimuth=solar_position["azimuth"],
        dni=weather["dni"].to_numpy(),
        ghi=weather["ghi"].to_numpy(),
        dhi=weather["dhi"].to_numpy(),
        albedo=weather["albedo"].to_numpy(),
    )
    poa_global = poa["poa_global"].fillna(0).clip(lower=0)
    cell_temp = weather["temp_air"].to_numpy() + poa_global.to_numpy() / 800 * 25

    dc_w = (
        panel_count
        * panel_power_w
        * (poa_global.to_numpy() / 1000)
        * (1 + temperature_coefficient * (cell_temp - 25))
        * (1 - system_losses)
    )
    dc_w = np.clip(dc_w, 0, None)
    ac_w = np.minimum(dc_w, inverter_ac_w) * inverter_efficiency
    ac_w = np.clip(ac_w, 0, None)

    dc_kw = panel_count * panel_power_w / 1000
    annual_kwh = float(ac_w.sum() / 1000)
    poa_kwh_m2 = float(poa_global.sum() / 1000)
    specific_yield = annual_kwh / dc_kw if dc_kw else 0.0
    performance_ratio = annual_kwh / (dc_kw * poa_kwh_m2) if dc_kw and poa_kwh_m2 else 0.0
    capacity_factor = annual_kwh / (dc_kw * 8760) if dc_kw else 0.0

    monthly_series = pd.Series(ac_w, index=times).groupby(times.month).sum() / 1000
    monthly = [
        {"month": int(month), "kwh": round(float(monthly_series.get(month, 0.0)), 2)}
        for month in range(1, 13)
    ]

    return {
        "annual_kwh": round(annual_kwh, 2),
        "specific_yield": round(specific_yield, 2),
        "performance_ratio": round(performance_ratio, 4),
        "capacity_factor": round(capacity_factor, 4),
        "poa_kwh_m2": round(poa_kwh_m2, 2),
        "dc_kw": round(dc_kw, 3),
        "ac_kw": round(inverter_ac_w / 1000, 3),
        "monthly": monthly,
        "hours": int(len(times)),
    }
