"""Autenticación local basada en sesión y PBKDF2."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User

_ITERATIONS = 240_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _ITERATIONS
    )
    return f"pbkdf2_sha256${_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, digest = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        )
        return hmac.compare_digest(candidate.hex(), digest)
    except (ValueError, TypeError):
        return False


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user and verify_password(password, user.password_hash):
        return user
    return None


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    user = db.get(User, int(user_id))
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


def require_api_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Sesión no iniciada")
    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Sesión no válida")
    return user
