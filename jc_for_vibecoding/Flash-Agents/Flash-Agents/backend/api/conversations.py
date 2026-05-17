from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from ..auth import audit, get_current_user
from ..config import settings
from ..database import SessionLocal, get_db
from ..models import Conversation, ConversationMessage, User
from ..schemas import ConversationCreate, ConversationMessageOut, ConversationOut, ConversationUpdate, MessageRequest, QuestionAnswerIn
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


def _save_message(db: Session, conversation: Conversation, user: User, role: str, content: str, *, event_type: str | None = None, meta: dict | None = None) -> ConversationMessage:
    message = ConversationMessage(
        conversation_id=conversation.id,
        user_id=user.id,
        role=role,
        content=content,
        event_type=event_type,
        meta=meta or {},
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def _decode_sse_data(item: dict) -> tuple[str, dict | str | None]:
    event_name = str(item.get("event") or "message")
    raw = item.get("data")
    if isinstance(raw, str):
        try:
            return event_name, json.loads(raw)
        except json.JSONDecodeError:
            return event_name, raw
    return event_name, raw


def _collect_assistant_event(meta: dict, event_name: str, data: dict | str | None, chunks: list[str]) -> None:
    if event_name == "assistant.delta" and isinstance(data, dict):
        chunks.append(str(data.get("text") or ""))
    elif event_name == "reasoning" and isinstance(data, dict):
        meta.setdefault("reasoning", []).append(str(data.get("text") or ""))
    elif event_name == "todo.update" and isinstance(data, dict):
        meta["todos"] = data.get("items") or []
    elif event_name in {"tool.start", "tool.end"} and isinstance(data, dict):
        meta.setdefault("tools", []).append({"event": event_name, **data})
    elif event_name == "question" and isinstance(data, dict):
        meta.setdefault("questions", []).append(data)


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


@router.get("/{conversation_id}/messages", response_model=list[ConversationMessageOut])
async def list_messages(conversation_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ConversationMessage]:
    conv = _get_conversation(db, user, conversation_id)
    return list(
        db.scalars(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conv.id, ConversationMessage.user_id == user.id)
            .order_by(ConversationMessage.created_at, ConversationMessage.id)
            .limit(500)
        )
    )


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


@router.post("/{conversation_id}/questions/{question_id}/answer")
async def answer_question(conversation_id: str, question_id: str, payload: QuestionAnswerIn, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, bool]:
    conv = _get_conversation(db, user, conversation_id)
    await opencode_client.answer_question(conv, question_id, payload.answer)
    audit(db, actor=user, action="question.answer", resource_type="conversation", resource_id=conv.id, domain=user.domain, request=request, details={"question_id": question_id})
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
            _save_message(db, conv, db_user, "user", payload.content, event_type="message", meta={"client_message_id": payload.client_message_id})

            audit(db, actor=db_user, action="message.send", resource_type="conversation", resource_id=conv.id, domain=db_user.domain, request=request, details={"agent_id": conv.agent_id, "client_message_id": payload.client_message_id})

            assistant_chunks: list[str] = []
            assistant_meta: dict = {}
            async for item in opencode_client.ask(db_user, conv, payload.content, db):
                if await request.is_disconnected():
                    break
                event_name, data = _decode_sse_data(item)
                _collect_assistant_event(assistant_meta, event_name, data, assistant_chunks)
                yield item
            assistant_content = "".join(assistant_chunks)
            if assistant_content or assistant_meta:
                _save_message(db, conv, db_user, "assistant", assistant_content, event_type="assistant", meta=assistant_meta)
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
