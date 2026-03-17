from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "openai-chat-compat-gateway"
    host: str = "0.0.0.0"
    port: int = 8000
    log_dir: Path = Field(default_factory=lambda: Path(os.getenv("LOG_DIR", "./logs")))
    bridge_dir: Path = Field(default_factory=lambda: Path(os.getenv("BRIDGE_DIR", "./bridge_files")))
    bridge_route: str = os.getenv("BRIDGE_ROUTE", "/bridge/files")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
    bridge_public_url_base: Optional[str] = os.getenv("BRIDGE_PUBLIC_URL_BASE") or None
    bridge_use_relative_path_in_url: bool = (
        os.getenv("BRIDGE_USE_RELATIVE_PATH_IN_URL", "false").lower() == "true"
    )
    generated_image_name_prefix: str = os.getenv("GENERATED_IMAGE_NAME_PREFIX", "upload_")
    download_remote_images: bool = os.getenv("DOWNLOAD_REMOTE_IMAGES", "true").lower() == "true"
    remote_image_timeout_seconds: float = float(os.getenv("REMOTE_IMAGE_TIMEOUT_SECONDS", "15"))
    session_store_file: Path = Field(default_factory=lambda: Path(os.getenv("SESSION_STORE_FILE", "./sessions.json")))
    stateful_by_default: bool = os.getenv("STATEFUL_BY_DEFAULT", "false").lower() == "true"
    log_pretty_json: bool = os.getenv("LOG_PRETTY_JSON", "true").lower() == "true"
    prompt_append_tools: bool = os.getenv("PROMPT_APPEND_TOOLS", "false").lower() == "true"
    backend_user_fallback: str = os.getenv("BACKEND_USER_FALLBACK", "openai-compat-user")
    stream_include_usage_by_default: bool = (
        os.getenv("STREAM_INCLUDE_USAGE_BY_DEFAULT", "true").lower() == "true"
    )

    def ensure_dirs(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.bridge_dir.mkdir(parents=True, exist_ok=True)
        self.session_store_file.parent.mkdir(parents=True, exist_ok=True)

    @property
    def resolved_bridge_public_url_base(self) -> str:
        if self.bridge_public_url_base:
            return self.bridge_public_url_base.rstrip("/")
        return f"{self.public_base_url.rstrip('/')}{self.bridge_route}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
