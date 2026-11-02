from __future__ import annotations

import math
import tomllib
import zipfile
from pathlib import Path

from docx import Document as DocxDocument
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Design, Document, Equipment
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
    site_page = auth_client.get(f"/projects/{project_id}/site")
    assert site_page.status_code == 200
    assert 'id="edit-nodes"' in site_page.text
    assert 'id="area-readout"' in site_page.text

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

    memory_response = auth_client.post(
        f"/designs/{design_id}/documents/memory", follow_redirects=False
    )
    assert memory_response.status_code == 303
    bidding_response = auth_client.post(
        f"/designs/{design_id}/documents/bidding", follow_redirects=False
    )
    assert bidding_response.status_code == 303
    assert auth_client.get(f"/projects/{project_id}/documents").status_code == 200

    with SessionLocal() as db:
        documents = list(
            db.scalars(select(Document).where(Document.design_id == design_id)).all()
        )
        assert {document.kind for document in documents} == {
            "memoria_calculo",
            "pliego_licitacion",
        }
        for document in documents:
            assert Path(document.docx_path).exists()
            assert Path(document.toml_path).exists()
            snapshot = tomllib.loads(
                Path(document.toml_path).read_text(encoding="utf-8")
            )
            assert snapshot["project"]["name"] == "Proyecto de prueba"
            assert snapshot["document_type"] == document.kind
        memory = next(
            document for document in documents if document.kind == "memoria_calculo"
        )
        bidding = next(
            document for document in documents if document.kind == "pliego_licitacion"
        )
        assert memory.pdf_path and Path(memory.pdf_path).exists()
        assert bidding.pdf_path and Path(bidding.pdf_path).exists()

        with zipfile.ZipFile(memory.docx_path) as archive:
            memory_xml = archive.read("word/document.xml").decode("utf-8")
        with zipfile.ZipFile(bidding.docx_path) as archive:
            bidding_xml = archive.read("word/document.xml").decode("utf-8")
        assert "{{" not in memory_xml and "{%" not in memory_xml
        assert "{{" not in bidding_xml and "{%" not in bidding_xml

        memory_doc = DocxDocument(memory.docx_path)
        bidding_doc = DocxDocument(bidding.docx_path)
        assert len(memory_doc.tables) >= 15
        assert len(memory_doc.inline_shapes) >= 11
        assert "Pliegos Técnicos" in "\n".join(
            paragraph.text for paragraph in bidding_doc.paragraphs
        )

    memory_pdf = auth_client.get(f"/documents/{memory.id}/download/pdf")
    assert memory_pdf.status_code == 200
    assert memory_pdf.headers["content-type"].startswith("application/pdf")

    geojson_response = auth_client.get(f"/api/projects/{project_id}/export.geojson")
    assert geojson_response.status_code == 200
    assert geojson_response.json()["type"] == "FeatureCollection"

    area_response = auth_client.post(
        "/api/geometry/area", json={"geojson": ROOF}
    )
    assert area_response.status_code == 200
    assert area_response.json()["valid"] is True
    assert 280 <= area_response.json()["area_m2"] <= 320

    invalid_polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [LON, LAT],
                [LON + DELTA_LON, LAT + DELTA_LAT],
                [LON + DELTA_LON, LAT],
                [LON, LAT + DELTA_LAT],
                [LON, LAT],
            ]
        ],
    }
    invalid_area = auth_client.post(
        "/api/geometry/area", json={"geojson": invalid_polygon}
    )
    assert invalid_area.status_code == 200
    assert invalid_area.json()["valid"] is False

    obstacle_response = auth_client.post(
        f"/api/roofs/{roof_id}/obstacles",
        json={
            "name": "Chimenea",
            "geojson": ROOF,
            "height_m": 1.5,
            "kind": "chimenea",
        },
    )
    assert obstacle_response.status_code == 200
    obstacle_id = obstacle_response.json()["id"]
    site_page = auth_client.get(f"/projects/{project_id}/site")
    assert "Chimenea" in site_page.text
    assert "obstacle-edit" in site_page.text
    update_obstacle = auth_client.put(
        f"/api/obstacles/{obstacle_id}",
        json={
            "name": "Chimenea editada",
            "geojson": ROOF,
            "height_m": 2.0,
            "kind": "ducto",
        },
    )
    assert update_obstacle.status_code == 200
    delete_obstacle = auth_client.delete(f"/api/obstacles/{obstacle_id}")
    assert delete_obstacle.status_code == 200

    moved_roof = {
        "type": "Polygon",
        "coordinates": [
            [
                [LON, LAT],
                [LON + DELTA_LON * 1.1, LAT],
                [LON + DELTA_LON, LAT + DELTA_LAT],
                [LON, LAT + DELTA_LAT],
                [LON, LAT],
            ]
        ],
    }
    update_roof = auth_client.put(
        f"/api/roofs/{roof_id}",
        json={
            "name": "Techumbre de prueba",
            "geojson": moved_roof,
            "tilt_deg": 20,
            "azimuth_deg": 180,
            "material": "Techumbre metálica",
            "usable_factor": 0.9,
        },
    )
    assert update_roof.status_code == 200
    assert update_roof.json()["invalidated_designs"] >= 1

    with SessionLocal() as db:
        design = db.get(Design, design_id)
        assert design is not None
        assert design.status == "desactualizado"

    stale_simulation = auth_client.post(
        f"/designs/{design_id}/simulate", follow_redirects=False
    )
    assert stale_simulation.status_code == 303
    assert "techumbre" in stale_simulation.headers["location"].lower()

    stale_financial = auth_client.post(
        f"/designs/{design_id}/financial", follow_redirects=False
    )
    assert stale_financial.status_code == 303
    assert "techumbre" in stale_financial.headers["location"].lower()

    stale_documents = auth_client.post(
        f"/designs/{design_id}/documents/memory", follow_redirects=False
    )
    assert stale_documents.status_code == 303
    assert "techumbre" in stale_documents.headers["location"].lower()
