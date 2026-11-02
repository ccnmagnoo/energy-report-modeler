from __future__ import annotations

import math

import pytest
from shapely.geometry import shape

from app.services.finance import analyze, annual_savings, irr, npv
from app.services.geometry import area_m2, as_polygon
from app.services.layout import generate_layout

LAT = -33.314975
LON = -71.414803
DELTA_LAT = 15 / 111_320
DELTA_LON = 20 / (111_320 * math.cos(math.radians(LAT)))
ROOF = {
    "type": "Polygon",
    "coordinates": [
        [
            [LON, LAT],
            [LON + DELTA_LON, LAT],
            [LON + DELTA_LON, LAT + DELTA_LAT],
            [LON, LAT + DELTA_LAT],
            [LON, LAT],
        ]
    ],
}


def test_area_is_metric_and_reasonable():
    measured = area_m2(ROOF, LAT, LON)
    assert 280 <= measured <= 320


def test_layout_stays_inside_roof_and_counts_panels():
    result = generate_layout(ROOF, 1.038, 2.384, tilt_deg=20, latitude=LAT, longitude=LON)
    assert result["count"] > 0
    assert result["occupancy"] > 0
    polygon = as_polygon(ROOF).buffer(0.01)
    for feature in result["geojson"]["features"]:
        panel = shape(feature["geometry"])
        assert panel.within(polygon)


def test_financial_indicators():
    assert npv(0.1, [-1000, 500, 500, 500]) == pytest.approx(243.43, abs=0.1)
    assert irr([-1000, 500, 500, 500]) == pytest.approx(0.2337, abs=0.001)

    savings = annual_savings(60_000, 50_000, 150)
    assert savings == pytest.approx(50_000 * 150 + 10_000 * 150 * 0.5)

    result = analyze(
        capex_clp=40_000_000,
        annual_savings_clp=6_000_000,
        annual_opex_clp=400_000,
        annual_kwh=60_000,
        years=25,
        discount_rate=0.08,
    )
    assert result["npv_clp"] > 0
    assert result["irr"] and result["irr"] > 0
    assert result["lcoe_clp_kwh"] > 0
