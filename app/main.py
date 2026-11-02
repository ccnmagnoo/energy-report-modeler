"""Aplicación FastAPI local del Modelador de Reportes FV."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_KEY
from app.db import SessionLocal, init_db
from app.routers import api, auth, catalog, dashboard, designs, documents, projects
from app.seed import ensure_seed
from app.web import STATIC_DIR, TEMPLATES_DIR


@asynccontextmanager
async def lifespan(_: FastAPI):
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    with SessionLocal() as db:
        ensure_seed(db)
    yield


app = FastAPI(
    title="Modelador de Reportes FV",
    description="MVP local para estudios, memorias de cálculo y documentos fotovoltaicos.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    same_site="lax",
    https_only=False,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(projects.router)
app.include_router(catalog.router)
app.include_router(designs.router)
app.include_router(documents.router)
app.include_router(api.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": "Modelador de Reportes FV", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
