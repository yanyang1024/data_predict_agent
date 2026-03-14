from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

from .config import Settings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TraceLogger:
    def __init__(self, settings: Settings, trace_id: Optional[str] = None):
        self.settings = settings
        self.trace_id = trace_id or uuid.uuid4().hex
        date_dir = datetime.now().strftime("%Y%m%d")
        self.trace_dir = settings.log_dir / date_dir / self.trace_id
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.trace_dir / "events.jsonl"
        self.backend_sse_raw_path = self.trace_dir / "backend_raw_sse.txt"
        self.emitted_sse_path = self.trace_dir / "emitted_openai_sse.txt"
        self._setup_app_logger()

    def _setup_app_logger(self) -> None:
        self.app_logger = logging.getLogger("openai_compat_gateway")
        if self.app_logger.handlers:
            return
        self.app_logger.setLevel(logging.INFO)
        log_path = self.settings.log_dir / "app.log"
        handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        self.app_logger.addHandler(handler)

    def save_json(self, filename: str, data: Any) -> Path:
        path = self.trace_dir / filename
        with path.open("w", encoding="utf-8") as f:
            if self.settings.log_pretty_json:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(data, f, ensure_ascii=False)
        return path

    def append_text(self, filename: str, text: str) -> Path:
        path = self.trace_dir / filename
        with path.open("a", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")
        return path

    def event(self, stage: str, payload: Any, status: str = "ok", **extra: Any) -> None:
        record: Dict[str, Any] = {
            "ts": utc_now_iso(),
            "trace_id": self.trace_id,
            "stage": stage,
            "status": status,
            "payload": payload,
        }
        if extra:
            record.update(extra)
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.app_logger.info("trace_id=%s stage=%s status=%s", self.trace_id, stage, status)

    def log_backend_raw_sse(self, line: str) -> None:
        self.append_text("backend_raw_sse.txt", line)
        self.event("backend_sse_line_raw", {"line": line})

    def log_emitted_sse(self, line: str) -> None:
        self.append_text("emitted_openai_sse.txt", line)
        self.event("openai_sse_line_emitted", {"line": line})
