from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .api import admin, agents, auth, conversations, files, instance, skills
from .config import settings
from .database import SessionLocal, init_db
from .services.instance_manager import idle_reaper_loop, sync_systemd_template

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("flash-agents")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup step 1/4: validating env and directories")
    settings.ensure_runtime_dirs()
    if settings.JWT_SECRET == "change-me-in-production" and settings.ENV == "production":
        raise RuntimeError("JWT_SECRET must be changed in production")

    logger.info("startup step 2/4: creating database tables")
    await init_db()

    logger.info("startup step 3/4: syncing systemd template")
    await sync_systemd_template()

    logger.info("startup step 4/4: starting idle instance reaper")
    task = asyncio.create_task(idle_reaper_loop(SessionLocal))
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title=settings.APP_NAME, default_response_class=ORJSONResponse, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(agents.router, prefix=settings.API_PREFIX)
app.include_router(conversations.router, prefix=settings.API_PREFIX)
app.include_router(files.router, prefix=settings.API_PREFIX)
app.include_router(skills.router, prefix=settings.API_PREFIX)
app.include_router(instance.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}
