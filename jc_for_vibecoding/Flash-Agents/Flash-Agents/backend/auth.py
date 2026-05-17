from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
from fastapi import Depends, Header, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import AuditLog, User


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: str, claims: dict[str, Any]) -> tuple[str, int]:
    expires = _now() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "exp": int(expires.timestamp()),
        "iat": int(_now().timestamp()),
        **claims,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, settings.JWT_EXPIRE_MINUTES * 60


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def load_whitelist() -> dict[str, Any]:
    """Read whitelist.json on every auth request so allow-list changes are hot-loaded."""

    path: Path = settings.whitelist_path
    if not path.exists():
        return {"users": [], "domains": settings.ALLOWED_DOMAINS}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Invalid whitelist.json: {exc}") from exc


def normalize_domain(domain: str | None) -> str:
    value = (domain or settings.DEFAULT_DOMAIN).strip().upper()
    allowed = {d.upper() for d in settings.ALLOWED_DOMAINS}
    if value not in allowed:
        raise HTTPException(status_code=403, detail="Domain is not allowed")
    return value


def resolve_whitelist_user(email: str, domain: str | None = None) -> dict[str, Any] | None:
    whitelist = load_whitelist()
    email_lower = email.lower()
    for item in whitelist.get("users", []):
        if str(item.get("email", "")).lower() == email_lower:
            if item.get("disabled"):
                raise HTTPException(status_code=403, detail="User is disabled")
            return item
    allowed_domains = {str(d).upper() for d in whitelist.get("domains", settings.ALLOWED_DOMAINS)}
    if settings.AUTH_ALLOW_UNLISTED and normalize_domain(domain) in allowed_domains:
        return None
    raise HTTPException(status_code=403, detail="User is not in whitelist")


def upsert_user_from_claims(db: Session, claims: dict[str, Any]) -> User:
    email = str(claims.get("email") or claims.get("sub") or "").lower()
    if not email:
        raise HTTPException(status_code=401, detail="SSO profile has no email")

    whitelist_item = resolve_whitelist_user(email, claims.get("domain"))
    domain = normalize_domain((whitelist_item or {}).get("domain") or claims.get("domain"))
    roles = (whitelist_item or {}).get("roles") or claims.get("roles") or []
    is_admin = bool((whitelist_item or {}).get("is_admin") or claims.get("is_admin") or "admin" in roles)
    employee_no = (whitelist_item or {}).get("employee_no") or claims.get("employee_no")
    display_name = (whitelist_item or {}).get("display_name") or claims.get("display_name") or email.split("@")[0]
    external_id = str(claims.get("sub") or email)
    normalized_employee_no = int(employee_no) if employee_no not in (None, "") else None

    user = db.scalar(select(User).where(User.email == email))
    if normalized_employee_no is not None:
        employee_owner = db.scalar(select(User).where(User.employee_no == normalized_employee_no, User.email != email))
        if employee_owner is not None:
            raise HTTPException(status_code=409, detail="Employee number already exists and would collide with an OpenCode port")
    if user is None:
        user = User(external_id=external_id, email=email, display_name=display_name, domain=domain)
        db.add(user)
    user.external_id = external_id
    user.display_name = display_name
    user.domain = domain
    user.employee_no = normalized_employee_no
    user.roles = {"roles": list(roles) if isinstance(roles, list) else [str(roles)]}
    user.is_admin = is_admin
    user.disabled = bool((whitelist_item or {}).get("disabled", False))
    db.commit()
    db.refresh(user)
    return user


def extract_token(authorization: str | None, token: str | None) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    if token:
        return token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
) -> User:
    raw = extract_token(authorization, token)
    claims = decode_access_token(raw)
    user = upsert_user_from_claims(db, claims)
    if user.disabled:
        raise HTTPException(status_code=403, detail="User is disabled")
    request.state.user = user
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permission required")
    return user


def audit(db: Session, *, actor: User | None, action: str, resource_type: str, resource_id: str, domain: str, request: Request | None = None, details: dict[str, Any] | None = None) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor.id if actor else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            domain=domain,
            ip=request.client.host if request and request.client else "",
            user_agent=request.headers.get("user-agent", "") if request else "",
            details=details or {},
        )
    )
    db.commit()
