from __future__ import annotations

import math
import tomllib
from pathlib import Path

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Document, Equipment
from app.services.weather import _synthetic_weather

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


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_and_main_pages(auth_client):
    assert auth_client.get("/").status_code == 200
    assert auth_client.get("/projects").status_code == 200
    assert auth_client.get("/catalog").status_code == 200


def test_full_vertical_flow(auth_client, monkeypatch):
    response = auth_client.post(
        "/projects",
        data={
            "name": "Proyecto de prueba",
            "code": "TEST-001",
            "client_name": "Organismo público",
            "client_rut": "61.000.000-0",
            "connection_type": "netbilling",
            "annual_consumption_kwh": "80000",
            "tariff_clp_kwh": "150",
            "discount_rate": "8",
            "analysis_years": "25",
            "opex_pct": "1",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    project_id = int(response.headers["location"].rsplit("/", 1)[-1])

    roof_response = auth_client.post(
        f"/api/projects/{project_id}/roofs",
        json={
            "name": "Techumbre de prueba",
            "geojson": ROOF,
            "tilt_deg": 20,
            "azimuth_deg": 180,
            "material": "Techumbre metálica",
            "usable_factor": 0.9,
        },
    )
    assert roof_response.status_code == 200
    roof_id = roof_response.json()["id"]
    assert auth_client.get(f"/projects/{project_id}/site").status_code == 200

    with SessionLocal() as db:
        panel = db.scalar(select(Equipment).where(Equipment.category == "Panel"))
        inverter = db.scalar(select(Equipment).where(Equipment.category == "Inversor"))
        assert panel is not None and inverter is not None
        panel_id, inverter_id = panel.id, inverter.id

    design_response = auth_client.post(
        f"/projects/{project_id}/designs",
        data={
            "roof_id": roof_id,
            "panel_id": panel_id,
            "inverter_id": inverter_id,
            "tilt_deg": "20",
            "azimuth_deg": "180",
            "name": "Diseño de prueba",
        },
        follow_redirects=False,
    )
    assert design_response.status_code == 303
    design_id = int(design_response.headers["location"].rsplit("/", 1)[-1])
    assert auth_client.get(f"/designs/{design_id}").status_code == 200

    monkeypatch.setattr(
        "app.routers.designs.get_weather",
        lambda *args, **kwargs: {
            "dataframe": _synthetic_weather(2024),
            "source": "Synthetic test",
            "year": 2024,
            "warning": None,
        },
    )

    simulate_response = auth_client.post(
        f"/designs/{design_id}/simulate", follow_redirects=False
    )
    assert simulate_response.status_code == 303

    financial_response = auth_client.post(
        f"/designs/{design_id}/financial", follow_redirects=False
    )
    assert financial_response.status_code == 303

    documents_response = auth_client.post(
        f"/designs/{design_id}/documents", follow_redirects=False
    )
    assert documents_response.status_code == 303
    assert auth_client.get(f"/projects/{project_id}/documents").status_code == 200

    with SessionLocal() as db:
        document = db.scalar(
            select(Document).where(Document.design_id == design_id).order_by(Document.id.desc())
        )
        assert document is not None
        assert Path(document.docx_path).exists()
        assert Path(document.pdf_path).exists()
        assert Path(document.toml_path).exists()
        document_id = document.id
        toml_path = Path(document.toml_path)
        snapshot = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        assert snapshot["project"]["name"] == "Proyecto de prueba"
        assert snapshot["simulation"]["annual_kwh"] > 0

    pdf_response = auth_client.get(f"/documents/{document_id}/download/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"].startswith("application/pdf")

    geojson_response = auth_client.get(f"/api/projects/{project_id}/export.geojson")
    assert geojson_response.status_code == 200
    assert geojson_response.json()["type"] == "FeatureCollection"
