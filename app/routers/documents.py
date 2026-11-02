from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.auth import require_user
from app.db import get_db
from app.models import Document, User
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/documents/{document_id}/download/{kind}")
def download_document(
    document_id: int,
    kind: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    mapping = {
        "docx": (document.docx_path, "memoria_calculo.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        "pdf": (document.pdf_path, "memoria_calculo.pdf", "application/pdf"),
        "toml": (document.toml_path, "resultados.toml", "application/toml"),
    }
    if kind not in mapping:
        raise HTTPException(status_code=400, detail="Formato no soportado")

    path_value, filename, media_type = mapping[kind]
    if not path_value:
        raise HTTPException(status_code=404, detail="Archivo no disponible")
    path = Path(path_value)
    if not path.exists():
        raise HTTPException(status_code=404, detail="El archivo ya no existe en disco")

    return FileResponse(path, filename=filename, media_type=media_type)
