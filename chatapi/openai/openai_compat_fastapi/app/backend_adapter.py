from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional


# =========================
# 你需要在这里接入真实后端函数
# =========================

def create_conversation() -> str:
    """
    真实环境请从你现有项目中 import 这个函数。
    示例：from your_backend_module import create_conversation
    """
    raise NotImplementedError("Please import your real create_conversation() here.")



def chat_query_v2_sse(
    user_id: str,
    app_conversation_id: str,
    content: str,
    query_extends: Optional[Dict[str, Any]] = None,
):
    """
    真实环境请从你现有项目中 import 这个函数。
    如果你当前版本只有 (user_id, app_conversation_id, content) 三个参数，
    可以保留原函数不动，然后让 ExistingServiceAdapter 自动 fallback。
    """
    raise NotImplementedError("Please import your real chat_query_v2_sse() here.")


class ExistingServiceAdapter:
    def __init__(
        self,
        create_conversation_fn: Callable[[], str] = create_conversation,
        chat_query_v2_sse_fn: Callable[..., Any] = chat_query_v2_sse,
    ) -> None:
        self.create_conversation_fn = create_conversation_fn
        self.chat_query_v2_sse_fn = chat_query_v2_sse_fn

    def create_conversation(self) -> str:
        return self.create_conversation_fn()

    def chat_query_v2_sse(
        self,
        user_id: str,
        app_conversation_id: str,
        content: str,
        query_extends: Optional[Dict[str, Any]] = None,
    ) -> Any:
        # 优先尝试显式 query_extends / QueryExtends 适配；失败后退化成拼接到 Query
        try:
            return self.chat_query_v2_sse_fn(
                user_id=user_id,
                app_conversation_id=app_conversation_id,
                content=content,
                query_extends=query_extends,
            )
        except TypeError:
            pass

        try:
            return self.chat_query_v2_sse_fn(
                user_id=user_id,
                app_conversation_id=app_conversation_id,
                content=content,
                QueryExtends=query_extends,
            )
        except TypeError:
            pass

        if query_extends:
            content = (
                f"{content}\n\n[QueryExtends as plain text fallback]\n"
                + json.dumps(query_extends, ensure_ascii=False, indent=2)
            )
        return self.chat_query_v2_sse_fn(
            user_id=user_id,
            app_conversation_id=app_conversation_id,
            content=content,
        )


# =========================
# 以下是 mock，方便本地测试
# =========================
@dataclass
class MockSSEResponse:
    status_code: int
    lines: List[str]

    def iter_lines(self, chunk_size: int = 4) -> Iterable[bytes]:
        del chunk_size
        for line in self.lines:
            yield line.encode("utf-8")


class MockBackendAdapter(ExistingServiceAdapter):
    def __init__(self) -> None:
        super().__init__(self._create_conv, self._chat)
        self._counter = 0

    def _create_conv(self) -> str:
        self._counter += 1
        return f"mock-conv-{self._counter:04d}"

    def _chat(
        self,
        user_id: str,
        app_conversation_id: str,
        content: str,
        query_extends: Optional[Dict[str, Any]] = None,
    ) -> MockSSEResponse:
        del user_id
        text = self._build_answer(content=content, query_extends=query_extends)
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        now = int(time.time())
        out: List[str] = []
        out.append(
            "data:" + json.dumps(
                {
                    "event": "message_start",
                    "task_id": task_id,
                    "id": task_id,
                    "conversation_id": app_conversation_id,
                },
                ensure_ascii=False,
            )
        )
        out.append(
            "data:" + json.dumps(
                {
                    "event": "message_output_start",
                    "task_id": task_id,
                    "id": task_id,
                    "think_message_id": None,
                    "conversation_id": app_conversation_id,
                },
                ensure_ascii=False,
            )
        )
        for chunk in self._split_text(text):
            out.append(
                "data:" + json.dumps(
                    {
                        "event": "message",
                        "task_id": task_id,
                        "id": task_id,
                        "answer": chunk,
                        "created_at": str(now),
                        "think_message_id": None,
                        "conversation_id": app_conversation_id,
                    },
                    ensure_ascii=False,
                )
            )
        out.append(
            "data:" + json.dumps(
                {
                    "event": "message_output_end",
                    "task_id": task_id,
                    "id": task_id,
                    "think_message_id": None,
                    "conversation_id": app_conversation_id,
                },
                ensure_ascii=False,
            )
        )
        out.append(
            "data:" + json.dumps(
                {
                    "event": "message_cost",
                    "task_id": task_id,
                    "id": task_id,
                    "input_tokens": max(len(content) // 4, 1),
                    "output_tokens": max(len(text) // 2, 1),
                    "created_at": now,
                    "conversation_id": app_conversation_id,
                },
                ensure_ascii=False,
            )
        )
        out.append(
            "data:" + json.dumps(
                {
                    "event": "message_end",
                    "task_id": task_id,
                    "id": task_id,
                    "conversation_id": app_conversation_id,
                },
                ensure_ascii=False,
            )
        )
        return MockSSEResponse(status_code=200, lines=out)

    @staticmethod
    def _split_text(text: str) -> List[str]:
        if len(text) <= 1:
            return [text]
        # 用 2 字符切分，方便测试流式 chunk
        return [text[i : i + 2] for i in range(0, len(text), 2)]

    @staticmethod
    def _build_answer(content: str, query_extends: Optional[Dict[str, Any]]) -> str:
        if query_extends and query_extends.get("Files"):
            file_count = len(query_extends["Files"])
            return f"已收到文本与 {file_count} 张图片，兼容服务转发成功。"
        if "tool_call_id" in content or "assistant(tool_calls)" in content or "role=tool" in content:
            return "已收到带 tool call / tool message 的上下文，兼容服务转发成功。"
        return "简单文本消息转发成功。"
