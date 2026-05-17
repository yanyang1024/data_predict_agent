from __future__ import annotations

import csv
import io
from datetime import timezone, timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models import AuditLog, Conversation, User
from ..schemas import AdminStatsOut
from ..services.instance_manager import instance_manager

router = APIRouter(prefix="/admin", tags=["admin"])


def _parse_tz(value: str) -> timezone:
    sign = 1 if value.startswith("+") else -1
    parts = value[1:].split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    return timezone(sign * timedelta(hours=hours, minutes=minutes))


@router.get("/stats", response_model=AdminStatsOut)
async def stats(db: Session = Depends(get_db), _admin: User = Depends(require_admin)) -> AdminStatsOut:
    users = db.scalar(select(func.count(User.id))) or 0
    conversations = db.scalar(select(func.count(Conversation.id)).where(Conversation.deleted_at.is_(None))) or 0
    rows = db.execute(select(User.domain, func.count(User.id)).group_by(User.domain)).all()
    return AdminStatsOut(users=users, conversations=conversations, running_instances=instance_manager.running_count(), domains={domain: count for domain, count in rows})


@router.get("/users")
async def users(db: Session = Depends(get_db), _admin: User = Depends(require_admin)) -> list[dict]:
    rows = db.scalars(select(User).order_by(User.domain, User.email)).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "display_name": u.display_name,
            "domain": u.domain,
            "employee_no": u.employee_no,
            "is_admin": u.is_admin,
            "disabled": u.disabled,
            "created_at": u.created_at,
        }
        for u in rows
    ]


@router.get("/audit")
async def audit_logs(limit: int = Query(default=200, le=1000), db: Session = Depends(get_db), _admin: User = Depends(require_admin)) -> list[dict]:
    rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)).all()
    return [
        {
            "id": r.id,
            "actor_user_id": r.actor_user_id,
            "action": r.action,
            "resource_type": r.resource_type,
            "resource_id": r.resource_id,
            "domain": r.domain,
            "created_at": r.created_at,
            "details": r.details,
        }
        for r in rows
    ]


@router.get("/audit.csv")
async def audit_csv(tz: str = "+08:00", limit: int = Query(default=5000, le=50000), db: Session = Depends(get_db), _admin: User = Depends(require_admin)) -> StreamingResponse:
    local_tz = _parse_tz(tz)
    rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "actor_user_id", "action", "resource_type", "resource_id", "domain", "created_at", "ip", "user_agent"])
    for r in rows:
        created = r.created_at.astimezone(local_tz).isoformat() if r.created_at else ""
        writer.writerow([r.id, r.actor_user_id, r.action, r.resource_type, r.resource_id, r.domain, created, r.ip, r.user_agent])
    content = "\ufeff" + buf.getvalue()
    return StreamingResponse(iter([content]), media_type="text/csv; charset=utf-8-sig", headers={"Content-Disposition": "attachment; filename=audit.csv"})
