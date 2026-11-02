from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth import require_user
from app.db import get_db
from app.models import Equipment, User
from app.web import templates

router = APIRouter()


@router.get("/catalog", response_class=HTMLResponse)
def catalog(
    request: Request,
    q: str = "",
    category: str = "",
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    statement = select(Equipment).where(Equipment.active.is_(True))
    if category:
        statement = statement.where(Equipment.category == category)
    if q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(
            or_(Equipment.manufacturer.ilike(term), Equipment.model.ilike(term))
        )
    equipment = list(
        db.scalars(statement.order_by(Equipment.category, Equipment.manufacturer)).all()
    )
    categories = list(
        db.scalars(
            select(Equipment.category).distinct().order_by(Equipment.category)
        ).all()
    )
    return templates.TemplateResponse(
        request=request,
        name="catalog/list.html",
        context={
            "request": request,
            "user": user,
            "equipment": equipment,
            "categories": categories,
            "q": q,
            "category": category,
        },
    )
