from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth import require_admin, require_user
from app.db import get_db
from app.models import Equipment, User
from app.routers.utils import to_float, to_int
from app.services.audit import log
from app.web import templates

router = APIRouter()

CATEGORY_ORDER = ["Panel", "Inversor", "Estructura", "Batería", "Otro"]
CATEGORY_LABELS = {
    "Panel": "Paneles",
    "Inversor": "Inversores",
    "Estructura": "Estructuras",
    "Batería": "Baterías",
    "Otro": "Otros",
}
CATEGORY_SINGULAR = {
    "Panel": "panel",
    "Inversor": "inversor",
    "Estructura": "estructura",
    "Batería": "batería",
    "Otro": "equipo",
}
CURRENCIES = ["CLP", "USD", "EUR", "UF", "UTM", "GBP", "BRL"]


def _equipment(db: Session, equipment_id: int) -> Equipment:
    item = db.get(Equipment, equipment_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return item


def _value(form, key: str, default: str = "") -> str:
    return str(form.get(key, default) or "").strip()


def _optional_float(form, key: str) -> float | None:
    raw = _value(form, key)
    if raw == "":
        return None
    return to_float(raw, 0.0)


def _specs_from_form(category: str, form) -> dict:
    specs: dict = {}
    if category == "Panel":
        for key in ("vmp", "imp", "voc", "isc", "temp_coef"):
            value = _optional_float(form, key)
            if value is not None:
                specs[key] = value
        warranty = _value(form, "warranty_years")
        if warranty:
            specs["warranty_years"] = to_int(warranty, 0)
        if _value(form, "cell_type"):
            specs["cell_type"] = _value(form, "cell_type")
    elif category == "Inversor":
        for key in ("max_dc_w", "mppt_min", "mppt_max", "max_voltage", "max_input_current"):
            value = _optional_float(form, key)
            if value is not None:
                specs[key] = value
        mppt_count = _value(form, "mppt_count")
        if mppt_count:
            specs["mppt_count"] = to_int(mppt_count, 0)
        if _value(form, "phases"):
            specs["phases"] = _value(form, "phases")
    elif category == "Estructura":
        for key in ("roof_type", "mounting"):
            if _value(form, key):
                specs[key] = _value(form, key)
    elif category == "Batería":
        for key in ("capacity_kwh", "voltage", "depth_of_discharge"):
            value = _optional_float(form, key)
            if value is not None:
                specs[key] = value
        if _value(form, "chemistry"):
            specs["chemistry"] = _value(form, "chemistry")
    else:
        if _value(form, "notes"):
            specs["notes"] = _value(form, "notes")
    return specs


def _apply_form(equipment: Equipment, form, category: str) -> None:
    equipment.category = category
    equipment.manufacturer = _value(form, "manufacturer")
    equipment.model = _value(form, "model")
    equipment.price_clp = to_float(_value(form, "price_clp"), 0.0)
    equipment.currency = _value(form, "currency", "CLP") or "CLP"
    equipment.datasheet_url = _value(form, "datasheet_url") or None
    equipment.power_w = to_float(_value(form, "power_w"), 0.0)
    equipment.efficiency = to_float(_value(form, "efficiency"), 0.0)
    equipment.width_mm = to_float(_value(form, "width_mm"), 0.0)
    equipment.height_mm = to_float(_value(form, "height_mm"), 0.0)
    equipment.specs = _specs_from_form(category, form)
    equipment.active = form.get("active") in {"on", "true", "1"}


def _validate(equipment: Equipment) -> str | None:
    if equipment.category not in CATEGORY_ORDER:
        return "Categoría no válida."
    if not equipment.manufacturer:
        return "El fabricante es obligatorio."
    if not equipment.model:
        return "El modelo es obligatorio."
    if equipment.price_clp < 0:
        return "El precio no puede ser negativo."
    if equipment.power_w < 0 or equipment.efficiency < 0:
        return "La potencia y eficiencia no pueden ser negativas."
    if equipment.width_mm < 0 or equipment.height_mm < 0:
        return "Las dimensiones no pueden ser negativas."
    return None


def _duplicate(db: Session, equipment: Equipment) -> Equipment | None:
    statement = select(Equipment).where(
        Equipment.category == equipment.category,
        Equipment.manufacturer == equipment.manufacturer,
        Equipment.model == equipment.model,
    )
    if equipment.id:
        statement = statement.where(Equipment.id != equipment.id)
    return db.scalar(statement.limit(1))


def _form_context(
    request: Request,
    user: User,
    equipment: Equipment,
    error: str | None,
    title: str,
    action: str,
) -> dict:
    return {
        "request": request,
        "user": user,
        "equipment": equipment,
        "error": error,
        "title": title,
        "action": action,
        "categories": CATEGORY_ORDER,
        "category_labels": CATEGORY_LABELS,
        "category_singular": CATEGORY_SINGULAR,
        "currencies": CURRENCIES,
    }


@router.get("/catalog", response_class=HTMLResponse)
def catalog(
    request: Request,
    q: str = "",
    category: str = "",
    status: str = "active",
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    statement = select(Equipment)
    if status == "active":
        statement = statement.where(Equipment.active.is_(True))
    elif status == "archived":
        statement = statement.where(Equipment.active.is_(False))
    if category:
        statement = statement.where(Equipment.category == category)
    if q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Equipment.manufacturer.ilike(term),
                Equipment.model.ilike(term),
                Equipment.category.ilike(term),
            )
        )
    equipment = list(
        db.scalars(
            statement.order_by(Equipment.category, Equipment.manufacturer, Equipment.model)
        ).all()
    )
    grouped = {name: [] for name in CATEGORY_ORDER}
    for item in equipment:
        grouped.setdefault(item.category, []).append(item)
    return templates.TemplateResponse(
        request=request,
        name="catalog/list.html",
        context={
            "request": request,
            "user": user,
            "is_admin": user.role == "admin",
            "grouped": grouped,
            "category_order": CATEGORY_ORDER,
            "category_labels": CATEGORY_LABELS,
            "category_singular": CATEGORY_SINGULAR,
            "categories": CATEGORY_ORDER,
            "q": q,
            "category": category,
            "status": status,
            "total": len(equipment),
        },
    )


@router.get("/catalog/new", response_class=HTMLResponse)
def new_equipment(
    request: Request,
    category: str = "Panel",
    user: User = Depends(require_admin),
):
    if category not in CATEGORY_ORDER:
        category = "Panel"
    equipment = Equipment(
        category=category,
        manufacturer="",
        model="",
        price_clp=0.0,
        currency="CLP",
        active=True,
        specs={},
    )
    return templates.TemplateResponse(
        request=request,
        name="catalog/form.html",
        context=_form_context(
            request,
            user,
            equipment,
            None,
            f"Nuevo {CATEGORY_SINGULAR[category]}",
            "/catalog/new",
        ),
    )


@router.post("/catalog/new", response_class=HTMLResponse)
async def create_equipment(
    request: Request,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    form = await request.form()
    category = _value(form, "category", "Panel")
    equipment = Equipment(category=category, specs={})
    _apply_form(equipment, form, category)
    error = _validate(equipment)
    if error is None and _duplicate(db, equipment):
        error = "Ya existe un equipo con esa categoría, fabricante y modelo."
    if error:
        return templates.TemplateResponse(
            request=request,
            name="catalog/form.html",
            context=_form_context(
                request,
                user,
                equipment,
                error,
                f"Nuevo {CATEGORY_SINGULAR.get(category, 'equipo')}",
                "/catalog/new",
            ),
            status_code=400,
        )
    db.add(equipment)
    db.flush()
    log(db, user, "equipment", equipment.id, "created", {"category": category, "model": equipment.model})
    db.commit()
    return RedirectResponse("/catalog?notice=Equipo+creado", status_code=303)


@router.get("/catalog/{equipment_id}/edit", response_class=HTMLResponse)
def edit_equipment(
    equipment_id: int,
    request: Request,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    equipment = _equipment(db, equipment_id)
    return templates.TemplateResponse(
        request=request,
        name="catalog/form.html",
        context=_form_context(
            request,
            user,
            equipment,
            None,
            f"Editar {CATEGORY_SINGULAR.get(equipment.category, 'equipo')}",
            f"/catalog/{equipment.id}/edit",
        ),
    )


@router.post("/catalog/{equipment_id}/edit", response_class=HTMLResponse)
async def update_equipment(
    equipment_id: int,
    request: Request,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    equipment = _equipment(db, equipment_id)
    form = await request.form()
    category = _value(form, "category", equipment.category)
    _apply_form(equipment, form, category)
    error = _validate(equipment)
    if error is None and _duplicate(db, equipment):
        error = "Ya existe un equipo con esa categoría, fabricante y modelo."
    if error:
        return templates.TemplateResponse(
            request=request,
            name="catalog/form.html",
            context=_form_context(
                request,
                user,
                equipment,
                error,
                f"Editar {CATEGORY_SINGULAR.get(category, 'equipo')}",
                f"/catalog/{equipment.id}/edit",
            ),
            status_code=400,
        )
    log(db, user, "equipment", equipment.id, "updated", {"category": category, "model": equipment.model})
    db.commit()
    return RedirectResponse("/catalog?notice=Equipo+actualizado", status_code=303)


@router.post("/catalog/{equipment_id}/archive")
def archive_equipment(
    equipment_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    equipment = _equipment(db, equipment_id)
    equipment.active = False
    log(db, user, "equipment", equipment.id, "archived", {"model": equipment.model})
    db.commit()
    return RedirectResponse("/catalog?notice=Equipo+archivado", status_code=303)


@router.post("/catalog/{equipment_id}/restore")
def restore_equipment(
    equipment_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    equipment = _equipment(db, equipment_id)
    equipment.active = True
    log(db, user, "equipment", equipment.id, "restored", {"model": equipment.model})
    db.commit()
    return RedirectResponse("/catalog?notice=Equipo+restaurado", status_code=303)
