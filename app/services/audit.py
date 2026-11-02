"""Registro de auditoría local."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import AuditEvent, User


def log(
    db: Session,
    actor: User | None,
    entity: str,
    entity_id: int | None,
    action: str,
    details: dict | None = None,
) -> None:
    db.add(
        AuditEvent(
            org_id=actor.org_id if actor else None,
            actor_id=actor.id if actor else None,
            entity=entity,
            entity_id=entity_id,
            action=action,
            details_json=details or {},
        )
    )
