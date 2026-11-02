from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import require_user
from app.db import get_db
from app.models import Design, Document, Project, User
from app.web import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    projects = list(
        db.scalars(select(Project).order_by(Project.updated_at.desc()).limit(8)).all()
    )
    stats = {
        "projects": db.scalar(select(func.count(Project.id))) or 0,
        "designs": db.scalar(select(func.count(Design.id))) or 0,
        "documents": db.scalar(select(func.count(Document.id))) or 0,
        "kw": db.scalar(select(func.sum(Design.dc_kw))) or 0,
    }
    latest_designs = list(
        db.scalars(
            select(Design).order_by(Design.created_at.desc(), Design.id.desc()).limit(5)
        ).all()
    )
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "user": user,
            "projects": projects,
            "stats": stats,
            "latest_designs": latest_designs,
        },
    )
