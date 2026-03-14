from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .backend_adapter import ExistingServiceAdapter, MockBackendAdapter
from .config import get_settings
from .schemas import ChatCompletionRequest
from .service import CompatibilityService
from .session_store import FileSessionStore
from .trace_logger import TraceLogger


settings = get_settings()
backend_adapter: ExistingServiceAdapter
if os.getenv("USE_MOCK_BACKEND", "true").lower() == "true":
    backend_adapter = MockBackendAdapter()
else:
    backend_adapter = ExistingServiceAdapter()

session_store = FileSessionStore(settings.session_store_file)
compat_service = CompatibilityService(settings=settings, backend=backend_adapter, session_store=session_store)


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    settings.ensure_dirs()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount(settings.bridge_route, StaticFiles(directory=settings.bridge_dir), name="bridge-files")


@app.get("/healthz")
def healthz() -> dict:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "bridge_route": settings.bridge_route,
        "public_base_url": settings.public_base_url,
        "using_mock_backend": isinstance(backend_adapter, MockBackendAdapter),
    }


@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: Request,
    x_session_id: Optional[str] = Header(default=None),
    x_app_conversation_id: Optional[str] = Header(default=None),
):
    trace = TraceLogger(settings=settings)
    raw_body = await request.body()
    raw_text = raw_body.decode("utf-8")
    trace.append_text("request_raw.json", raw_text)

    try:
        body = ChatCompletionRequest.model_validate_json(raw_text)
    except Exception as exc:  # noqa: BLE001
        trace.event("request_parse_failed", {"error": str(exc), "raw_text": raw_text}, status="error")
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "message": f"Invalid request body: {exc}",
                    "type": "invalid_request_error",
                }
            },
            headers={"X-Trace-ID": trace.trace_id},
        )

    trace.save_json("request_parsed.json", body.model_dump(exclude_none=True))
    trace.event("request_received", body.model_dump(exclude_none=True))

    try:
        conversation_id = compat_service.resolve_conversation_id(
            request=body,
            x_session_id=x_session_id,
            x_app_conversation_id=x_app_conversation_id,
            trace=trace,
        )
        backend_request = compat_service.build_backend_request(body, conversation_id, trace)
        backend_response = compat_service.call_backend(body, backend_request, trace)

        headers = {
            "X-Trace-ID": trace.trace_id,
            "X-App-Conversation-ID": conversation_id,
            "Cache-Control": "no-cache",
        }
        if body.stream:
            return StreamingResponse(
                compat_service.stream_openai_response(body, backend_response, trace),
                media_type="text/event-stream",
                headers=headers,
            )

        response = compat_service.to_openai_response(body, backend_response, trace)
        return JSONResponse(content=response, headers=headers)
    except Exception as exc:  # noqa: BLE001
        trace.event("request_failed", {"error": str(exc)}, status="error")
        status_code = getattr(exc, "status_code", 500)
        detail = getattr(exc, "detail", str(exc))
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "message": detail,
                    "type": "backend_error" if status_code >= 500 else "invalid_request_error",
                }
            },
            headers={"X-Trace-ID": trace.trace_id},
        )
