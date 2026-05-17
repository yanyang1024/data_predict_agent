from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Conversation, User
from .agent_manager import agent_manager
from .instance_manager import instance_manager


@dataclass
class SseItem:
    event: str
    data: dict[str, Any]

    def as_event(self) -> dict[str, str]:
        return {"event": self.event, "data": json.dumps(self.data, ensure_ascii=False)}


class OpenCodeClient:
    def __init__(self) -> None:
        self._abort_events: dict[str, asyncio.Event] = {}

    def _base_url(self, port: int) -> str:
        return f"http://127.0.0.1:{port}{settings.OPENCODE_API_PREFIX.rstrip('/')}"

    def _sandbox_cwd(self, conversation: Conversation) -> str:
        return f"/workspace/{conversation.id}"

    def _abort_event(self, conversation_id: str) -> asyncio.Event:
        event = self._abort_events.get(conversation_id)
        if event is None:
            event = asyncio.Event()
            self._abort_events[conversation_id] = event
        return event

    async def ensure_session(self, user: User, conversation: Conversation, db: Session) -> tuple[str, int]:
        state = await instance_manager.ensure_instance(user, db=db)
        if conversation.opencode_session_id and not conversation.opencode_session_id.startswith("mock-"):
            instance_manager.touch(user.id)
            return conversation.opencode_session_id, state.port

        agent = agent_manager.get_agent(conversation.agent_id, user.domain)
        payload = {
            "title": conversation.title,
            "cwd": self._sandbox_cwd(conversation),
            "hostCwd": conversation.workspace_path,
            "agent": conversation.agent_id,
            "systemPrompt": agent.system_prompt if agent else "",
            "domain": user.domain,
            "userId": user.id,
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(f"{self._base_url(state.port)}/sessions", json=payload)
                resp.raise_for_status()
                data = resp.json()
                session_id = str(data.get("id") or data.get("session_id") or "")
                if not session_id:
                    raise RuntimeError("OpenCode session response has no id")
        except Exception:
            if not settings.OPENCODE_MOCK_ON_FAILURE:
                raise
            return f"mock-{uuid.uuid4()}", state.port

        conversation.opencode_session_id = session_id
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation.opencode_session_id, state.port

    def _parse_sse_line(self, state: dict[str, Any], line: str) -> SseItem | None:
        if not line:
            data = "\n".join(state.get("data", []))
            event = state.get("event", "message")
            state.clear()
            if not data:
                return None
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                payload = {"text": data}
            return SseItem(event=event, data=payload)
        if line.startswith(":"):
            return None
        if line.startswith("event:"):
            state["event"] = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            state.setdefault("data", []).append(line.split(":", 1)[1].lstrip())
        return None

    async def _mock_stream(self, conversation: Conversation, prompt: str) -> AsyncGenerator[dict[str, str], None]:
        chunks = [
            "已接收任务。",
            "我会在隔离工作区中分析需求，",
            "调用相应 Agent 和技能，",
            "然后返回结果。",
        ]
        yield SseItem("reasoning", {"text": "OpenCode 不可达，已启用本地 mock 流。"}).as_event()
        yield SseItem("todo.update", {"items": [{"id": "1", "text": "解析用户输入", "status": "done"}, {"id": "2", "text": "执行任务", "status": "running"}]}).as_event()
        for chunk in chunks:
            if self._abort_event(conversation.id).is_set():
                yield SseItem("aborted", {"conversation_id": conversation.id}).as_event()
                return
            await asyncio.sleep(0.15)
            yield SseItem("assistant.delta", {"text": chunk}).as_event()
        yield SseItem("tool.start", {"name": "workspace", "input": {"path": conversation.workspace_path}}).as_event()
        await asyncio.sleep(0.1)
        yield SseItem("tool.end", {"name": "workspace", "output": "workspace ready"}).as_event()
        yield SseItem("done", {"conversation_id": conversation.id}).as_event()

    async def ask(self, user: User, conversation: Conversation, prompt: str, db: Session) -> AsyncGenerator[dict[str, str], None]:
        event = self._abort_event(conversation.id)
        event.clear()
        session_id, port = await self.ensure_session(user, conversation, db)
        instance_manager.touch(user.id)
        yield SseItem("conversation.bound", {"conversation_id": conversation.id, "opencode_session_id": session_id, "port": port}).as_event()

        payload = {"message": prompt, "sessionId": session_id, "conversationId": conversation.id, "agent": conversation.agent_id}
        sse_state: dict[str, Any] = {}
        try:
            async with httpx.AsyncClient(timeout=settings.OPENCODE_REQUEST_TIMEOUT_SECONDS) as client:
                async with client.stream("POST", f"{self._base_url(port)}/sessions/{session_id}/messages", json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if event.is_set():
                            yield SseItem("aborted", {"conversation_id": conversation.id}).as_event()
                            return
                        parsed = self._parse_sse_line(sse_state, line)
                        if parsed:
                            yield parsed.as_event()
        except Exception as exc:
            if not settings.OPENCODE_MOCK_ON_FAILURE:
                yield SseItem("error", {"message": str(exc)}).as_event()
                return
            async for item in self._mock_stream(conversation, prompt):
                yield item

    async def recover_todo_state(self, conversation: Conversation) -> dict[str, Any]:
        if not conversation.opencode_session_id:
            return {"lost": False, "todos": []}
        state = instance_manager.status(conversation.user_id)
        if not state or not state.running:
            return {"lost": True, "todos": []}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self._base_url(state.port)}/sessions/{conversation.opencode_session_id}/todos")
                resp.raise_for_status()
                return {"lost": False, "todos": resp.json()}
        except Exception:
            return {"lost": True, "todos": []}

    async def abort(self, conversation: Conversation) -> None:
        # 6-step abort: flag -> API abort -> reject pending questions -> sleep -> close stream -> clean local state.
        event = self._abort_event(conversation.id)
        event.set()
        state = instance_manager.status(conversation.user_id)
        if state and state.running and conversation.opencode_session_id:
            base = self._base_url(state.port)
            async with httpx.AsyncClient(timeout=8) as client:
                for method, url, payload in [
                    ("POST", f"{base}/sessions/{conversation.opencode_session_id}/abort", {}),
                    ("POST", f"{base}/sessions/{conversation.opencode_session_id}/questions/reject", {"reason": "user_abort"}),
                ]:
                    try:
                        await client.request(method, url, json=payload)
                    except Exception:
                        pass
                await asyncio.sleep(0.2)
                try:
                    await client.post(f"{base}/sessions/{conversation.opencode_session_id}/close")
                except Exception:
                    pass
        self._abort_events.pop(conversation.id, None)

    async def answer_question(self, conversation: Conversation, question_id: str, answer: str) -> None:
        state = instance_manager.status(conversation.user_id)
        if not state or not state.running or not conversation.opencode_session_id:
            raise RuntimeError("OpenCode session is not running")
        base = self._base_url(state.port)
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.post(
                f"{base}/sessions/{conversation.opencode_session_id}/questions/{question_id}/answer",
                json={"answer": answer},
            )
            resp.raise_for_status()


opencode_client = OpenCodeClient()
