from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple

from fastapi import Header, HTTPException

from .backend_adapter import ExistingServiceAdapter
from .config import Settings
from .image_bridge import bridge_image_url
from .schemas import (
    BackendRequest,
    ChatCompletionRequest,
    ChatMessage,
    OpenAIChatCompletionChunk,
    OpenAIChatCompletionResponse,
    OpenAIChoice,
    OpenAIChoiceMessage,
    OpenAIChunkChoice,
    OpenAIChunkChoiceDelta,
    QueryExtendsInfo,
    UsageInfo,
)
from .session_store import FileSessionStore
from .sse_parser import ParsedSSEEvent, parse_sse_lines
from .trace_logger import TraceLogger


class CompatibilityService:
    def __init__(
        self,
        settings: Settings,
        backend: ExistingServiceAdapter,
        session_store: FileSessionStore,
    ) -> None:
        self.settings = settings
        self.backend = backend
        self.session_store = session_store

    def resolve_conversation_id(
        self,
        request: ChatCompletionRequest,
        x_session_id: Optional[str],
        x_app_conversation_id: Optional[str],
        trace: TraceLogger,
    ) -> str:
        if x_app_conversation_id:
            trace.event("conversation_id_resolved", {"source": "x_app_conversation_id", "value": x_app_conversation_id})
            return x_app_conversation_id

        session_key = x_session_id or (request.metadata or {}).get("session_key") or request.user
        stateful = bool(x_app_conversation_id or x_session_id or (request.metadata or {}).get("session_key"))
        stateful = stateful or self.settings.stateful_by_default
        if stateful and session_key:
            cached = self.session_store.get(session_key)
            if cached:
                trace.event("conversation_id_resolved", {"source": "session_store", "session_key": session_key, "value": cached})
                return cached

        conversation_id = self.backend.create_conversation()
        trace.event("conversation_id_created", {"value": conversation_id, "stateful": stateful, "session_key": session_key})
        if stateful and session_key:
            self.session_store.set(session_key, conversation_id)
            trace.event("conversation_id_persisted", {"session_key": session_key, "value": conversation_id})
        return conversation_id

    def build_backend_request(self, request: ChatCompletionRequest, conversation_id: str, trace: TraceLogger) -> BackendRequest:
        query_text, query_extends = self._flatten_messages(request=request, trace=trace)
        backend_request = BackendRequest(
            Query=query_text,
            AppConversationID=conversation_id,
            QueryExtends=QueryExtendsInfo(Files=query_extends) if query_extends else None,
        )
        trace.event("backend_request_built", backend_request.model_dump(exclude_none=True))
        return backend_request

    def _flatten_messages(self, request: ChatCompletionRequest, trace: TraceLogger) -> Tuple[str, List[Any]]:
        transcript_blocks: List[str] = []
        backend_files: List[Any] = []

        if request.tools and self.settings.prompt_append_tools:
            tools_text = json.dumps([tool.model_dump() for tool in request.tools], ensure_ascii=False, indent=2)
            transcript_blocks.append(f"[available_tools]\n{tools_text}")
            if request.tool_choice is not None:
                transcript_blocks.append(
                    f"[tool_choice]\n{json.dumps(request.tool_choice, ensure_ascii=False)}"
                )

        for idx, message in enumerate(request.messages):
            block, files = self._render_message_block(message=message, idx=idx, trace=trace)
            transcript_blocks.append(block)
            backend_files.extend(files)

        query_text = "\n\n".join(transcript_blocks).strip()
        trace.event(
            "messages_flattened",
            {
                "query_preview": query_text,
                "backend_file_count": len(backend_files),
            },
        )
        return query_text, backend_files

    def _render_message_block(self, message: ChatMessage, idx: int, trace: TraceLogger) -> Tuple[str, List[Any]]:
        parts: List[str] = [f"[message_{idx}]", f"role={message.role}"]
        if message.name:
            parts.append(f"name={message.name}")
        if message.tool_call_id:
            parts.append(f"tool_call_id={message.tool_call_id}")
        files: List[Any] = []

        if message.tool_calls:
            parts.append(
                "assistant(tool_calls)=\n" + json.dumps([tc.model_dump() for tc in message.tool_calls], ensure_ascii=False, indent=2)
            )

        content = message.content
        if isinstance(content, str):
            if content:
                parts.append(content)
        elif isinstance(content, list):
            text_parts: List[str] = []
            for part in content:
                if hasattr(part, "model_dump"):
                    part = part.model_dump()
                if not isinstance(part, dict):
                    text_parts.append(str(part))
                    continue
                ptype = part.get("type")
                if ptype == "text":
                    text_parts.append(part.get("text", ""))
                elif ptype == "image_url":
                    image_url = (part.get("image_url") or {}).get("url")
                    if image_url:
                        result = bridge_image_url(image_url, self.settings)
                        files.append(result.backend_file)
                        text_parts.append(f"[image] {result.backend_file.Url}")
                        trace.event(
                            "image_bridged",
                            {
                                "source": image_url[:128],
                                "public_url": result.backend_file.Url,
                                "name": result.backend_file.Name,
                                "size": result.backend_file.Size,
                            },
                        )
                else:
                    text_parts.append(json.dumps(part, ensure_ascii=False))
            if text_parts:
                parts.append("\n".join([p for p in text_parts if p]))
        elif content is not None:
            parts.append(str(content))

        if message.role == "tool":
            # 明确把 tool message 文本拼接进 Query，满足兼容要求
            parts.append("[tool_message_attached_to_query=true]")

        block = "\n".join([p for p in parts if p])
        return block, files

    def call_backend(self, request: ChatCompletionRequest, backend_request: BackendRequest, trace: TraceLogger) -> Any:
        user_id = request.user or self.settings.backend_user_fallback
        payload = backend_request.model_dump(exclude_none=True)
        trace.save_json("backend_forward_request.json", payload)
        trace.event("backend_request_forwarded", payload)
        response = self.backend.chat_query_v2_sse(
            user_id=user_id,
            app_conversation_id=backend_request.AppConversationID,
            content=backend_request.Query,
            query_extends=backend_request.QueryExtends.model_dump() if backend_request.QueryExtends else None,
        )
        trace.event(
            "backend_response_received",
            {"status_code": getattr(response, "status_code", None)},
        )
        status_code = getattr(response, "status_code", 200)
        if status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Backend returned status={status_code}")
        return response

    def iter_backend_events(self, backend_response: Any, trace: TraceLogger) -> Generator[ParsedSSEEvent, None, None]:
        lines = backend_response.iter_lines(chunk_size=4)
        for event in parse_sse_lines(lines):
            trace.log_backend_raw_sse(event.raw_line)
            trace.event("backend_sse_event_parsed", {"sse_event_name": event.sse_event_name, "data": event.data})
            yield event

    def to_openai_response(self, request: ChatCompletionRequest, backend_response: Any, trace: TraceLogger) -> Dict[str, Any]:
        text_parts: List[str] = []
        usage = UsageInfo()
        created = int(time.time())
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        final_task_id: Optional[str] = None

        for parsed in self.iter_backend_events(backend_response, trace):
            data = parsed.data or {}
            event_name = data.get("event")
            if data.get("task_id"):
                final_task_id = data["task_id"]
                completion_id = f"chatcmpl-{final_task_id}"
            created = _coerce_ts(data.get("created_at"), created)
            if event_name == "message":
                text_parts.append(data.get("answer", ""))
            elif event_name == "message_cost":
                prompt_tokens = int(data.get("input_tokens", 0) or 0)
                completion_tokens = int(data.get("output_tokens", 0) or 0)
                usage = UsageInfo(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                )
            elif event_name == "message_failed":
                raise HTTPException(status_code=502, detail=json.dumps(data, ensure_ascii=False))

        response = OpenAIChatCompletionResponse(
            id=completion_id,
            created=created,
            model=request.model,
            choices=[
                OpenAIChoice(
                    index=0,
                    message=OpenAIChoiceMessage(role="assistant", content="".join(text_parts)),
                    finish_reason="stop",
                )
            ],
            usage=usage,
        ).model_dump(exclude_none=True)
        trace.save_json("response_final.json", response)
        trace.event("openai_response_ready", response)
        return response

    def stream_openai_response(
        self,
        request: ChatCompletionRequest,
        backend_response: Any,
        trace: TraceLogger,
    ) -> Iterable[str]:
        created = int(time.time())
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        usage = UsageInfo()
        role_sent = False
        include_usage = request.stream_options.include_usage if request.stream_options and request.stream_options.include_usage is not None else self.settings.stream_include_usage_by_default

        for parsed in self.iter_backend_events(backend_response, trace):
            data = parsed.data or {}
            event_name = data.get("event")
            if data.get("task_id"):
                completion_id = f"chatcmpl-{data['task_id']}"
            created = _coerce_ts(data.get("created_at"), created)

            if event_name in {"message_output_start", "message_start"} and not role_sent:
                role_sent = True
                chunk = OpenAIChatCompletionChunk(
                    id=completion_id,
                    created=created,
                    model=request.model,
                    choices=[
                        OpenAIChunkChoice(
                            index=0,
                            delta=OpenAIChunkChoiceDelta(role="assistant"),
                            finish_reason=None,
                        )
                    ],
                ).model_dump(exclude_none=True)
                line = f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                trace.log_emitted_sse(line.rstrip("\n"))
                yield line
                continue

            if event_name == "message":
                if not role_sent:
                    role_sent = True
                    role_chunk = OpenAIChatCompletionChunk(
                        id=completion_id,
                        created=created,
                        model=request.model,
                        choices=[
                            OpenAIChunkChoice(
                                index=0,
                                delta=OpenAIChunkChoiceDelta(role="assistant"),
                                finish_reason=None,
                            )
                        ],
                    ).model_dump(exclude_none=True)
                    role_line = f"data: {json.dumps(role_chunk, ensure_ascii=False)}\n\n"
                    trace.log_emitted_sse(role_line.rstrip("\n"))
                    yield role_line
                delta_chunk = OpenAIChatCompletionChunk(
                    id=completion_id,
                    created=created,
                    model=request.model,
                    choices=[
                        OpenAIChunkChoice(
                            index=0,
                            delta=OpenAIChunkChoiceDelta(content=data.get("answer", "")),
                            finish_reason=None,
                        )
                    ],
                ).model_dump(exclude_none=True)
                delta_line = f"data: {json.dumps(delta_chunk, ensure_ascii=False)}\n\n"
                trace.log_emitted_sse(delta_line.rstrip("\n"))
                yield delta_line
                continue

            if event_name == "message_cost":
                prompt_tokens = int(data.get("input_tokens", 0) or 0)
                completion_tokens = int(data.get("output_tokens", 0) or 0)
                usage = UsageInfo(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                )
                continue

            if event_name == "message_end":
                stop_chunk = OpenAIChatCompletionChunk(
                    id=completion_id,
                    created=created,
                    model=request.model,
                    choices=[
                        OpenAIChunkChoice(
                            index=0,
                            delta=OpenAIChunkChoiceDelta(),
                            finish_reason="stop",
                        )
                    ],
                ).model_dump(exclude_none=True)
                stop_line = f"data: {json.dumps(stop_chunk, ensure_ascii=False)}\n\n"
                trace.log_emitted_sse(stop_line.rstrip("\n"))
                yield stop_line
                if include_usage:
                    usage_chunk = OpenAIChatCompletionChunk(
                        id=completion_id,
                        created=created,
                        model=request.model,
                        choices=[],
                        usage=usage,
                    ).model_dump(exclude_none=True)
                    usage_line = f"data: {json.dumps(usage_chunk, ensure_ascii=False)}\n\n"
                    trace.log_emitted_sse(usage_line.rstrip("\n"))
                    yield usage_line
                done_line = "data: [DONE]\n\n"
                trace.log_emitted_sse(done_line.rstrip("\n"))
                yield done_line
                trace.event(
                    "stream_done",
                    {"completion_id": completion_id, "usage": usage.model_dump()},
                )
                return

            if event_name == "message_failed":
                error_chunk = {
                    "error": {
                        "message": json.dumps(data, ensure_ascii=False),
                        "type": "backend_error",
                    }
                }
                error_line = f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
                trace.log_emitted_sse(error_line.rstrip("\n"))
                yield error_line
                done_line = "data: [DONE]\n\n"
                trace.log_emitted_sse(done_line.rstrip("\n"))
                yield done_line
                trace.event("stream_failed", data, status="error")
                return

        # 后端没有发 message_end 时，也保证正常收尾，避免客户端卡住。
        stop_chunk = OpenAIChatCompletionChunk(
            id=completion_id,
            created=created,
            model=request.model,
            choices=[
                OpenAIChunkChoice(index=0, delta=OpenAIChunkChoiceDelta(), finish_reason="stop")
            ],
        ).model_dump(exclude_none=True)
        stop_line = f"data: {json.dumps(stop_chunk, ensure_ascii=False)}\n\n"
        trace.log_emitted_sse(stop_line.rstrip("\n"))
        yield stop_line
        if include_usage:
            usage_chunk = OpenAIChatCompletionChunk(
                id=completion_id,
                created=created,
                model=request.model,
                choices=[],
                usage=usage,
            ).model_dump(exclude_none=True)
            usage_line = f"data: {json.dumps(usage_chunk, ensure_ascii=False)}\n\n"
            trace.log_emitted_sse(usage_line.rstrip("\n"))
            yield usage_line
        done_line = "data: [DONE]\n\n"
        trace.log_emitted_sse(done_line.rstrip("\n"))
        yield done_line
        trace.event("stream_done_without_message_end", {"completion_id": completion_id, "usage": usage.model_dump()})



def _coerce_ts(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
