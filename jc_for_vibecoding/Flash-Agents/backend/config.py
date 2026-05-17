from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment or backend/.env."""

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Flash-Agents"
    ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    CORS_ORIGINS: list[str] | str = ["http://localhost:5173", "http://127.0.0.1:5173"]

    DATABASE_URL: str = "mysql+pymysql://flash:flash@127.0.0.1:3306/flash_agents?charset=utf8mb4"
    DB_POOL_SIZE: int = 80
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_RECYCLE: int = 3600

    JWT_SECRET: str = Field(default="change-me-in-production", min_length=16)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 12

    SSO_ENABLED: bool = False
    SSO_AUTHORIZE_URL: str = ""
    SSO_TOKEN_URL: str = ""
    SSO_USERINFO_URL: str = ""
    SSO_CLIENT_ID: str = "flash-agents"
    SSO_CLIENT_SECRET: str = ""
    SSO_REDIRECT_URI: str = "http://localhost:5173/auth/callback"
    AUTH_ALLOW_UNLISTED: bool = True
    WHITELIST_PATH: str = "./backend/whitelist.json"

    WORKSPACE_ROOT: str = "./workspaces"
    SKILL_ROOT: str = "./skills_store"
    AGENT_ROOT: str = "./backend/agents"

    OPENCODE_BINARY: str = "opencode"
    OPENCODE_API_PREFIX: str = "/api"
    OPENCODE_BASE_PORT: int = 20000
    OPENCODE_DEFAULT_PORT: int = 4096
    OPENCODE_REQUEST_TIMEOUT_SECONDS: int = 60 * 60
    OPENCODE_MOCK_ON_FAILURE: bool = True

    SYSTEMD_ENABLED: bool = False
    SYSTEMD_TEMPLATE_NAME: str = "opencode@.service"
    SYSTEMD_USER_DIR: str = "~/.config/systemd/user"
    SYSTEMD_ENV_DIR: str = "~/.config/flash-agents/opencode"
    USER_SERVICE_NAME_TEMPLATE: str = "opencode@{user_id}.service"
    INSTANCE_MEMORY_MAX: str = "32G"
    INSTANCE_CPU_QUOTA: str = "200%"

    BWRAP_PATH: str = "bwrap"
    CGROUP_ENABLED: bool = True
    IDLE_TIMEOUT_SECONDS: int = 60 * 20
    IDLE_SCAN_SECONDS: int = 30
    HEARTBEAT_SECONDS: int = 15

    ALLOWED_DOMAINS: list[str] | str = ["RD", "MEC", "IT"]
    DEFAULT_DOMAIN: str = "IT"

    LOG_DIR: str = "./logs"

    @field_validator("CORS_ORIGINS", "ALLOWED_DOMAINS", mode="before")
    @classmethod
    def parse_list(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return value
        if value is None:
            return []
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                return [str(v).strip() for v in json.loads(raw)]
            return [v.strip() for v in raw.split(",") if v.strip()]
        return [str(value)]

    @property
    def workspace_root_path(self) -> Path:
        return Path(self.WORKSPACE_ROOT).expanduser().resolve()

    @property
    def skill_root_path(self) -> Path:
        return Path(self.SKILL_ROOT).expanduser().resolve()

    @property
    def agent_root_path(self) -> Path:
        return Path(self.AGENT_ROOT).expanduser().resolve()

    @property
    def whitelist_path(self) -> Path:
        return Path(self.WHITELIST_PATH).expanduser().resolve()

    @property
    def log_dir_path(self) -> Path:
        return Path(self.LOG_DIR).expanduser().resolve()

    def ensure_runtime_dirs(self) -> None:
        for path in [self.workspace_root_path, self.skill_root_path, self.agent_root_path, self.log_dir_path]:
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_runtime_dirs()
    return settings


settings = get_settings()
