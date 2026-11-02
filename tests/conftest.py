from __future__ import annotations

import os
import tempfile

TEST_DATA_DIR = tempfile.mkdtemp(prefix="fv-report-modeler-tests-")
os.environ["FV_DATA_DIR"] = TEST_DATA_DIR
os.environ["FV_DATABASE_URL"] = f"sqlite:///{TEST_DATA_DIR}/test.db"
os.environ["FV_WEATHER_OFFLINE"] = "1"
os.environ["FV_PDF_CONVERTER"] = "reportlab"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def auth_client(client):
    response = client.post(
        "/login",
        data={"email": "admin@local", "password": "admin123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    return client
