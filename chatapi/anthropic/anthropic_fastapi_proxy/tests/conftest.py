from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.store import session_store


@pytest.fixture(autouse=True)
def _isolate_dirs(tmp_path: Path):
    settings.log_dir = tmp_path / "logs"
    settings.media_dir = tmp_path / "media"
    settings.public_base_url = "http://testserver"
    settings.ensure_dirs()
    session_store.clear()
    yield
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
