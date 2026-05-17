from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    email: str
    display_name: str
    domain: str
    employee_no: int | None = None
    roles: dict[str, Any] = Field(default_factory=dict)
    is_admin: bool = False


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class DevLoginIn(BaseModel):
    email: str
    display_name: str | None = None
    domain: str = "IT"
    employee_no: int | None = None


class SsoCallbackIn(BaseModel):
    code: str
    state: str | None = None


class ConversationCreate(BaseModel):
    agent_id: str = "code"
    title: str | None = None


class ConversationUpdate(BaseModel):
    title: str | None = None
    agent_id: str | None = None


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: int
    domain: str
    agent_id: str
    title: str
    opencode_session_id: str | None = None
    workspace_path: str
    status: str
    last_error: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class MessageRequest(BaseModel):
    content: str
    conversation_id: str | None = None
    agent_id: str = "code"
    client_message_id: str | None = None
    attachments: list[dict[str, Any]] = Field(default_factory=list)


class FileWriteIn(BaseModel):
    path: str
    content: str
    encoding: str = "utf-8"


class FileOut(BaseModel):
    path: str
    name: str
    type: str
    size: int = 0
    updated_at: datetime | None = None


class FileReadOut(BaseModel):
    path: str
    content: str
    encoding: str


class AgentOut(BaseModel):
    id: str
    name: str
    description: str
    category: str = "general"
    domains: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    icon: str = "bot"
    system_prompt: str = ""


class SkillOut(BaseModel):
    id: int | str
    name: str
    version: str = "0.1.0"
    source: str
    domain: str
    entrypoint: str = "SKILL.md"
    enabled: bool = True
    manifest: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InstanceStatusOut(BaseModel):
    user_id: int
    service_name: str
    port: int
    running: bool
    last_seen: datetime | None = None
    mode: str


class AdminStatsOut(BaseModel):
    users: int
    conversations: int
    running_instances: int
    domains: dict[str, int]
