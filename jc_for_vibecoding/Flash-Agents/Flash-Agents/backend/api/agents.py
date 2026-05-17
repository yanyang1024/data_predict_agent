from __future__ import annotations

from fastapi import APIRouter, Depends, Header

from ..auth import get_current_user
from ..models import User
from ..schemas import AgentOut
from ..services.agent_manager import agent_manager

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentOut])
async def list_agents(accept_language: str | None = Header(default="zh-CN"), user: User = Depends(get_current_user)) -> list[dict]:
    return agent_manager.list_agents(user.domain, accept_language or "zh-CN")
