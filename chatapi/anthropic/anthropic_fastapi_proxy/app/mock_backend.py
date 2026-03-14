from __future__ import annotations

import json
import time
import uuid
from typing import Iterable, List, Optional


class MockResponse:
    def __init__(self, events: List[dict], status_code: int = 200):
        self._events = events
        self.status_code = status_code

    def iter_lines(self, chunk_size: int = 4) -> Iterable[bytes]:
        for event in self._events:
            yield f"data:{json.dumps(event, ensure_ascii=False)}".encode("utf-8")


def create_conversation() -> str:
    return f"conv_{uuid.uuid4().hex[:16]}"


def _answer_for(content: str, query_extends: Optional[dict]) -> str:
    if "<user_tool_result" in content:
        return "已收到工具结果，并继续基于工具结果回答。"
    if query_extends and query_extends.get("Files"):
        return "我已收到图片，并可以结合图片内容继续回答。"
    tail = content.split("\n")[-1].strip()
    if not tail:
        tail = "你好"
    return f"大模型兼容代理已收到：{tail}"


def chat_query_v2_sse(
    user_id: str,
    app_conversation_id: str,
    content: str,
    query_extends: Optional[dict] = None,
):
    task_id = uuid.uuid4().hex[:26]
    answer = _answer_for(content, query_extends)
    now = int(time.time())
    conv_id = app_conversation_id or create_conversation()
    events: List[dict] = [
        {
            "event": "message_start",
            "task_id": task_id,
            "id": task_id,
            "conversation_id": conv_id,
        },
        {
            "event": "message_output_start",
            "task_id": task_id,
            "id": task_id,
            "think_message_id": None,
            "conversation_id": conv_id,
        },
    ]
    for chunk in answer:
        events.append(
            {
                "event": "message",
                "task_id": task_id,
                "id": task_id,
                "answer": chunk,
                "created_at": str(now),
                "think_message_id": None,
                "conversation_id": conv_id,
            }
        )
    events.extend(
        [
            {
                "event": "message_output_end",
                "task_id": task_id,
                "id": task_id,
                "think_message_id": None,
                "conversation_id": conv_id,
            },
            {
                "event": "message_cost",
                "task_id": task_id,
                "id": task_id,
                "input_tokens": max(1, len(content) // 2),
                "output_tokens": max(1, len(answer)),
                "created_at": now,
                "conversation_id": conv_id,
            },
            {
                "event": "message_end",
                "task_id": task_id,
                "id": task_id,
                "conversation_id": conv_id,
                "agent_configuration": {"retriever_resource": {"enabled": False}},
            },
        ]
    )
    return MockResponse(events=events)
