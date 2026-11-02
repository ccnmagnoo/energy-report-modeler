"""Obtención de clima horario desde NASA POWER con caché local.

La aplicación usa internet para consultar NASA POWER. Si la consulta falla y
``FV_WEATHER_OFFLINE=1`` o no hay red, se genera un año sintético determinista
para no bloquear el flujo de demostración. El resultado siempre indica la
fuente utilizada.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from app.config import USER_AGENT, WEATHER_CACHE_DIR, WEATHER_OFFLINE, WEATHER_YEAR_OFFSET

NASA_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
PARAMETERS = [
    "ALLSKY_SFC_SW_DWN",
    "ALLSKY_SFC_SW_DNI",
    "ALLSKY_SFC_SW_DIFF",
    "T2M",
    "WS10M",
    "ALLSKY_SRF_ALB",
]


def _cache_path(latitude: float, longitude: float, year: int) -> Path:
    safe = f"{latitude:.4f}_{longitude:.4f}_{year}.json".replace("-", "m")
    return WEATHER_CACHE_DIR / safe


def _parse_payload(payload: dict, year: int) -> pd.DataFrame:
    parameters = payload["properties"]["parameter"]
    series: dict[str, pd.Series] = {}
    for name in PARAMETERS:
        values = parameters.get(name)
        if not values:
            continue
        series[name] = pd.Series(values, dtype="float64")

    if not series:
        raise ValueError("NASA POWER no devolvió parámetros utilizables")

    frame = pd.DataFrame(series)
    frame.index = pd.to_datetime(frame.index, format="%Y%m%d%H", errors="coerce")
    frame = frame[frame.index.notna()]
    frame = frame.replace(-999.0, np.nan)

    irradiance = ["ALLSKY_SFC_SW_DWN", "ALLSKY_SFC_SW_DNI", "ALLSKY_SFC_SW_DIFF"]
    for column in irradiance:
        if column in frame:
            frame[column] = frame[column].interpolate(limit_direction="both").fillna(0).clip(lower=0)
    if "T2M" in frame:
        frame["T2M"] = frame["T2M"].interpolate(limit_direction="both").fillna(15.0)
    if "WS10M" in frame:
        frame["WS10M"] = frame["WS10M"].interpolate(limit_direction="both").fillna(3.0)
    if "ALLSKY_SRF_ALB" in frame:
        frame["ALLSKY_SRF_ALB"] = frame["ALLSKY_SRF_ALB"].fillna(0.2).clip(0, 1)

    frame = frame.rename(
        columns={
            "ALLSKY_SFC_SW_DWN": "ghi",
            "ALLSKY_SFC_SW_DNI": "dni",
            "ALLSKY_SFC_SW_DIFF": "dhi",
            "T2M": "temp_air",
            "WS10M": "wind_speed",
            "ALLSKY_SRF_ALB": "albedo",
        }
    )
    frame["year"] = year
    return frame.sort_index()


def _fetch_nasa(latitude: float, longitude: float, year: int) -> pd.DataFrame:
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "RE",
        "latitude": latitude,
        "longitude": longitude,
        "start": f"{year}0101",
        "end": f"{year}1231",
        "format": "JSON",
        "time-standard": "LST",
    }
    response = requests.get(
        NASA_URL,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=90,
    )
    response.raise_for_status()
    payload = response.json()
    _cache_path(latitude, longitude, year).write_text(
        json.dumps(payload), encoding="utf-8"
    )
    return _parse_payload(payload, year)


def _synthetic_weather(year: int) -> pd.DataFrame:
    dates = pd.date_range(f"{year}-01-01", f"{year}-12-31 23:00", freq="h")
    day = dates.day_of_year.to_numpy()
    hour = dates.hour.to_numpy() + dates.minute.to_numpy() / 60
    altitude = np.sin(np.pi * (hour - 6) / 12)
    altitude = np.clip(altitude, 0, None)
    season = 0.72 + 0.28 * np.cos(2 * np.pi * (day - 172) / 365)
    solar = altitude * season
    frame = pd.DataFrame(
        {
            "ghi": 880 * solar,
            "dni": 720 * solar,
            "dhi": 110 * solar,
            "temp_air": 14 + 8 * np.sin(2 * np.pi * (day - 172) / 365) + 5 * solar,
            "wind_speed": np.full(len(dates), 3.0),
            "albedo": np.full(len(dates), 0.2),
        },
        index=dates,
    )
    frame["year"] = year
    return frame


def get_weather(
    latitude: float,
    longitude: float,
    year: int | None = None,
    allow_network: bool | None = None,
) -> dict:
    year = year or (datetime.now().year - WEATHER_YEAR_OFFSET)
    allow_network = (not WEATHER_OFFLINE) if allow_network is None else allow_network
    cache_file = _cache_path(latitude, longitude, year)

    if cache_file.exists():
        try:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            return {
                "dataframe": _parse_payload(payload, year),
                "source": "NASA POWER (caché)",
                "year": year,
                "warning": None,
            }
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            cache_file.unlink(missing_ok=True)

    if allow_network:
        try:
            return {
                "dataframe": _fetch_nasa(latitude, longitude, year),
                "source": "NASA POWER",
                "year": year,
                "warning": None,
            }
        except (requests.RequestException, ValueError, KeyError) as exc:
            return {
                "dataframe": _synthetic_weather(year),
                "source": "Sintético (respaldo)",
                "year": year,
                "warning": f"No fue posible consultar NASA POWER: {exc}",
            }

    return {
        "dataframe": _synthetic_weather(year),
        "source": "Sintético (offline)",
        "year": year,
        "warning": "FV_WEATHER_OFFLINE=1: se usó un año climático sintético.",
    }
