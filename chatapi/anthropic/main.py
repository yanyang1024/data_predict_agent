from __future__ import annotations

import json
import traceback
import uuid
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from .anthropic_mapper import build_upstream_request, update_session_after_success
from .config import settings
from .logging_utils import TraceLogger, logger
from .models import MessagesRequest
from .sse_bridge import build_non_streaming_message, iter_anthropic_stream
from .upstream_adapter import UpstreamSSEParser, backend

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.get("/proxy/media/{filename:path}")
def proxy_media(filename: str):
    path = settings.media_dir / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path)


@app.post("/v1/messages")
async def messages(
    request: Request,
    x_user_id: Optional[str] = Header(default=None),
    x_proxy_conversation_id: Optional[str] = Header(default=None),
    anthropic_version: Optional[str] = Header(default=None),
):
    trace_id = uuid.uuid4().hex
    trace = TraceLogger(trace_id)

    try:
        body_bytes = await request.body()
        raw_json = json.loads(body_bytes.decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"invalid request body: {exc}")

    trace.log("received_raw_request", raw_json, headers=dict(request.headers))

    try:
        req = MessagesRequest.model_validate(raw_json)
    except Exception as exc:
        trace.log("request_validation_error", {"error": str(exc)})
        raise HTTPException(status_code=400, detail=f"request validation failed: {exc}")

    user_id = x_user_id or (req.metadata or {}).get("user_id") or settings.default_user_id
    payload = build_upstream_request(req, user_id=user_id, proxy_conversation_id=x_proxy_conversation_id)
    trace.log("normalized_anthropic_request", req.model_dump(mode="json"))
    trace.log("upstream_forward_request_before_conversation", payload.model_dump(mode="json"))

    if not payload.app_conversation_id:
        try:
            payload.app_conversation_id = backend.create_conversation()
        except Exception as exc:
            trace.log("create_conversation_error", {"error": str(exc), "traceback": traceback.format_exc()})
            raise HTTPException(status_code=502, detail=f"create_conversation failed: {exc}")

    trace.log("upstream_forward_request", payload.model_dump(mode="json"))

    try:
        upstream_response = backend.chat_query_v2_sse(payload)
    except Exception as exc:
        trace.log("upstream_chat_error", {"error": str(exc), "traceback": traceback.format_exc()})
        raise HTTPException(status_code=502, detail=f"chat_query_v2_sse failed: {exc}")

    trace.log(
        "upstream_response_status",
        {"status_code": getattr(upstream_response, "status_code", None), "anthropic_version": anthropic_version},
    )

    parser = UpstreamSSEParser(trace)

    if settings.conversation_mode == "session":
        update_session_after_success(payload.proxy_conversation_id or "", payload.app_conversation_id, req)

    headers = {
        "anthropic-version": anthropic_version or "2023-06-01",
        "x-proxy-trace-id": trace_id,
        "x-proxy-conversation-id": payload.proxy_conversation_id or "",
        "x-upstream-app-conversation-id": payload.app_conversation_id,
    }

    if req.stream:
        generator = iter_anthropic_stream(req, parser.parse(upstream_response), trace)
        return StreamingResponse(generator, media_type="text/event-stream", headers=headers)

    response_json = build_non_streaming_message(req, parser.parse(upstream_response), trace)
    return JSONResponse(content=response_json, headers=headers)


@app.exception_handler(Exception)
async def catch_all(_: Request, exc: Exception):
    logger.exception("Unhandled proxy error: %s", exc)
    return JSONResponse(status_code=500, content={"type": "error", "error": str(exc)})
