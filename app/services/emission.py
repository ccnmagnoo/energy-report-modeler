"""Factor de emisión del SEN y cálculos de reducción de CO2."""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache

import numpy as np
import pandas as pd

from libs.emission_data import emission_data


@lru_cache(maxsize=1)
def _dataframe() -> pd.DataFrame:
    frame = pd.DataFrame(emission_data)
    frame["year"] = frame["year"].astype(int)
    frame["month"] = frame["month"].astype(int)
    frame["emission"] = (
        frame["emission"].astype(str).str.replace(",", ".", regex=False).astype(float)
    )
    return frame


def annual_avg() -> pd.DataFrame:
    return (
        _dataframe()[["year", "emission"]]
        .groupby("year", as_index=False)
        .mean()
        .sort_values("year")
    )


def annual_projection(year: int | None = None) -> float:
    year = year or (datetime.now().year + 1)
    data = annual_avg()
    if len(data) == 1:
        return float(data["emission"].iloc[0])
    coefficients = np.polyfit(data["year"].to_numpy(), data["emission"].to_numpy(), 1)
    value = float(np.polyval(coefficients, year))
    return max(0.0, value)


def historic() -> list[dict]:
    return [
        {"year": int(row.year), "factor_ton_mwh": round(float(row.emission), 4)}
        for row in annual_avg().itertuples()
    ]


def reduction_kg(energy_kwh: float, factor_ton_mwh: float) -> float:
    """1 Ton/MWh equivale a 1 kg/kWh, por lo que kWh × factor = kg CO2."""
    return max(0.0, energy_kwh * factor_ton_mwh)
