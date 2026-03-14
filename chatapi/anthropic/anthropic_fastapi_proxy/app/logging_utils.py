from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

from .config import settings


def setup_logging() -> logging.Logger:
    logger = logging.getLogger(settings.app_name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    file_handler = TimedRotatingFileHandler(
        filename=str(settings.log_dir / "app.log"),
        when="midnight",
        backupCount=14,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = setup_logging()


class TraceLogger:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        date_dir = settings.log_dir / "traces" / datetime.now().strftime("%Y%m%d")
        date_dir.mkdir(parents=True, exist_ok=True)
        self.path = date_dir / f"trace_{trace_id}.jsonl"

    def log(self, stage: str, payload: Any, **extra: Any) -> None:
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "trace_id": self.trace_id,
            "stage": stage,
            "payload": payload,
        }
        if extra:
            event["extra"] = extra
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
