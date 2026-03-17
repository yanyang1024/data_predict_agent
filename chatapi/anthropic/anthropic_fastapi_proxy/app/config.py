from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "anthropic-messages-compatible-proxy")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    log_dir: Path = Path(os.getenv("LOG_DIR", "./logs"))
    media_dir: Path = Path(os.getenv("MEDIA_DIR", "./media"))
    media_subdir: str = os.getenv("MEDIA_SUBDIR", "uploaded_images").strip("/")
    media_url_prefix: str = os.getenv("MEDIA_URL_PREFIX", "/proxy/media").rstrip("/")
    upload_filename_prefix: str = os.getenv("UPLOAD_FILENAME_PREFIX", "upload_rawpic")
    default_user_id: str = os.getenv("DEFAULT_USER_ID", "anthropic-proxy-user")
    conversation_mode: str = os.getenv("CONVERSATION_MODE", "stateless")  # stateless | session
    media_proxy_mode: str = os.getenv("MEDIA_PROXY_MODE", "download")  # download | passthrough
    expose_thinking_as_text: bool = os.getenv("EXPOSE_THINKING_AS_TEXT", "false").lower() == "true"
    use_mock_backend: bool = os.getenv("USE_MOCK_BACKEND", "true").lower() == "true"
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))

    def ensure_dirs(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        (self.media_dir / self.media_subdir).mkdir(parents=True, exist_ok=True)
        (self.log_dir / "traces").mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
