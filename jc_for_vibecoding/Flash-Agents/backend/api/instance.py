from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import InstanceStatusOut
from ..services.instance_manager import instance_manager

router = APIRouter(prefix="/instance", tags=["instance"])


@router.get("/me", response_model=InstanceStatusOut | dict)
async def my_instance(user: User = Depends(get_current_user)):
    state = instance_manager.status(user.id)
    if state is None:
        return {"user_id": user.id, "running": False, "mode": "none"}
    return state.__dict__


@router.post("/me/ensure", response_model=InstanceStatusOut)
async def ensure_my_instance(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    state = await instance_manager.ensure_instance(user, db=db)
    return state.__dict__


@router.post("/me/stop")
async def stop_my_instance(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, bool]:
    await instance_manager.stop_instance(user.id, db=db, reason="user_request")
    return {"ok": True}
