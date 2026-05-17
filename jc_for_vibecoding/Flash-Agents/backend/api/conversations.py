from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from ..auth import audit, get_current_user
from ..config import settings
from ..database import SessionLocal, get_db
from ..models import Conversation, User
from ..schemas import ConversationCreate, ConversationOut, ConversationUpdate, MessageRequest
from ..services.agent_manager import agent_manager
from ..services.opencode import opencode_client
from ..services.workspace import workspace_manager

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _get_conversation(db: Session, user: User, conversation_id: str) -> Conversation:
    conv = db.get(Conversation, conversation_id)
    if conv is None or conv.user_id != user.id or conv.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


def _new_title(content: str | None) -> str:
    if not content:
        return "新会话"
    clean = " ".join(content.strip().split())
    return (clean[:32] + "...") if len(clean) > 32 else clean


def _create_conversation(db: Session, user: User, agent_id: str, title: str | None = None) -> Conversation:
    if not agent_manager.get_agent(agent_id, user.domain):
        raise HTTPException(status_code=404, detail="Agent not found in current domain")
    conv = Conversation(user_id=user.id, domain=user.domain, agent_id=agent_id, title=title or "新会话", workspace_path="")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    workspace = workspace_manager.workspace_dir(user.id, conv.id)
    conv.workspace_path = str(workspace)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("", response_model=list[ConversationOut])
async def list_conversations(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Conversation]:
    return list(
        db.scalars(
            select(Conversation)
            .where(Conversation.user_id == user.id, Conversation.deleted_at.is_(None))
            .order_by(desc(Conversation.updated_at))
            .limit(200)
        )
    )


@router.post("", response_model=ConversationOut)
async def create_conversation(payload: ConversationCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Conversation:
    conv = _create_conversation(db, user, payload.agent_id, payload.title)
    audit(db, actor=user, action="conversation.create", resource_type="conversation", resource_id=conv.id, domain=user.domain, request=request)
    return conv


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Conversation:
    return _get_conversation(db, user, conversation_id)


@router.patch("/{conversation_id}", response_model=ConversationOut)
async def update_conversation(conversation_id: str, payload: ConversationUpdate, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Conversation:
    conv = _get_conversation(db, user, conversation_id)
    if payload.agent_id and payload.agent_id != conv.agent_id:
        if conv.opencode_session_id:
            raise HTTPException(status_code=409, detail="Cannot switch agent after OpenCode session is bound")
        if not agent_manager.get_agent(payload.agent_id, user.domain):
            raise HTTPException(status_code=404, detail="Agent not found")
        conv.agent_id = payload.agent_id
    if payload.title:
        conv.title = payload.title
    db.add(conv)
    db.commit()
    db.refresh(conv)
    audit(db, actor=user, action="conversation.update", resource_type="conversation", resource_id=conv.id, domain=user.domain, request=request)
    return conv


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, bool]:
    conv = _get_conversation(db, user, conversation_id)
    conv.deleted_at = datetime.now(timezone.utc)
    db.add(conv)
    db.commit()
    audit(db, actor=user, action="conversation.delete", resource_type="conversation", resource_id=conv.id, domain=user.domain, request=request)
    return {"ok": True}


@router.get("/{conversation_id}/orphan-check")
async def orphan_check(conversation_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    conv = _get_conversation(db, user, conversation_id)
    state = await opencode_client.recover_todo_state(conv)
    return {"conversation_id": conv.id, "opencode_session_id": conv.opencode_session_id, **state}


@router.post("/{conversation_id}/abort")
async def abort(conversation_id: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, bool]:
    conv = _get_conversation(db, user, conversation_id)
    await opencode_client.abort(conv)
    conv.status = "idle"
    db.add(conv)
    db.commit()
    audit(db, actor=user, action="conversation.abort", resource_type="conversation", resource_id=conv.id, domain=user.domain, request=request)
    return {"ok": True}


@router.post("/messages/stream")
async def stream_message(payload: MessageRequest, request: Request, user: User = Depends(get_current_user)) -> EventSourceResponse:
    """Fetch-stream compatible SSE endpoint. Conversation is bound to OpenCode only on first message."""

    async def event_generator():
        db = SessionLocal()
        try:
            db_user = db.get(User, user.id)
            if db_user is None:
                yield {"event": "error", "data": "User not found"}
                return
            if payload.conversation_id:
                conv = _get_conversation(db, db_user, payload.conversation_id)
            else:
                conv = _create_conversation(db, db_user, payload.agent_id, _new_title(payload.content))
            if conv.title == "新会话":
                conv.title = _new_title(payload.content)
            conv.status = "running"
            db.add(conv)
            db.commit()
            db.refresh(conv)

            audit(db, actor=db_user, action="message.send", resource_type="conversation", resource_id=conv.id, domain=db_user.domain, request=request, details={"agent_id": conv.agent_id, "client_message_id": payload.client_message_id})

            async for item in opencode_client.ask(db_user, conv, payload.content, db):
                if await request.is_disconnected():
                    break
                yield item
            conv.status = "idle"
            conv.updated_at = datetime.now(timezone.utc)
            db.add(conv)
            db.commit()
        except Exception as exc:
            yield {"event": "error", "data": str(exc)}
            try:
                if 'conv' in locals():
                    conv.status = "error"
                    conv.last_error = str(exc)
                    db.add(conv)
                    db.commit()
            except Exception:
                pass
        finally:
            db.close()

    return EventSourceResponse(event_generator(), ping=settings.HEARTBEAT_SECONDS)
