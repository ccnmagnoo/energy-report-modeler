"""Configuración local de la aplicación.

Todo se resuelve relativo a la raíz del repositorio para que la app pueda
ejecutarse con ``uvicorn app.main:app`` desde cualquier directorio.
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("FV_DATA_DIR", str(BASE_DIR / "data")))
DATABASE_URL = os.getenv("FV_DATABASE_URL", f"sqlite:///{DATA_DIR / 'app.db'}")
SECRET_KEY = os.getenv("FV_SECRET_KEY", "dev-only-change-this-secret")
DEFAULT_ADMIN_EMAIL = os.getenv("FV_ADMIN_EMAIL", "admin@local")
DEFAULT_ADMIN_PASSWORD = os.getenv("FV_ADMIN_PASSWORD", "admin123")
WEATHER_YEAR_OFFSET = int(os.getenv("FV_WEATHER_YEAR_OFFSET", "2"))
WEATHER_OFFLINE = os.getenv("FV_WEATHER_OFFLINE", "0") == "1"
USER_AGENT = os.getenv(
    "FV_USER_AGENT",
    "ModeladorReportesFV/0.1 (aplicacion local de estudios fotovoltaicos)",
)

DOCUMENTS_DIR = DATA_DIR / "projects"
CACHE_DIR = DATA_DIR / "cache"
WEATHER_CACHE_DIR = CACHE_DIR / "weather"
UPLOAD_DIR = DATA_DIR / "uploads"

for _directory in (DATA_DIR, DOCUMENTS_DIR, CACHE_DIR, WEATHER_CACHE_DIR, UPLOAD_DIR):
    _directory.mkdir(parents=True, exist_ok=True)
