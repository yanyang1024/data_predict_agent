from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class MessageParam(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: Literal["user", "assistant"]
    content: Union[str, List[Dict[str, Any]]]


class MessagesRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str
    max_tokens: int = Field(default=1024, ge=1)
    messages: List[MessageParam]
    stream: bool = False
    system: Optional[Union[str, List[Dict[str, Any]]]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class UpstreamFile(BaseModel):
    name: str
    path: str
    size: int
    url: str


class UpstreamQueryExtends(BaseModel):
    files: List[UpstreamFile] = Field(default_factory=list)


class UpstreamRequestPayload(BaseModel):
    user_id: str
    app_conversation_id: str
    content: str
    query_extends: UpstreamQueryExtends = Field(default_factory=UpstreamQueryExtends)
    proxy_conversation_id: Optional[str] = None
    mode: str = "stateless"


class SessionState(BaseModel):
    upstream_conversation_id: str
    last_forwarded_message_count: int = 0
    system_fingerprint: Optional[str] = None
