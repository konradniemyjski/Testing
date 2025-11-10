from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import models to register SQLAlchemy mappings before table creation
from . import models  # noqa: F401
from .db import Base, engine
from .schema_utils import ensure_project_code_column
from .routers import auth as auth_router
from .routers import projects as projects_router
from .routers import worklogs as worklogs_router

app = FastAPI(title="Worklog API", version="2.0.0")

default_allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
allowed_origins_env = os.getenv("CORS_ALLOW_ORIGINS")
if allowed_origins_env is not None:
    allowed_origins = [
        origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()
    ]
else:
    allowed_origins = default_allowed_origins

allow_origin_regex_env = os.getenv("CORS_ALLOW_ORIGIN_REGEX")
allow_origin_regex = (
    allow_origin_regex_env.strip()
    if allow_origin_regex_env and allow_origin_regex_env.strip()
    else r"https?://(localhost|127\.0\.0\.1)(:\d+)?$"
)

if allowed_origins == ["*"]:
    # Starlette disallows using wildcards together with a regex.
    allow_origin_regex = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_project_code_column(engine)


@app.get("/health", tags=["health"])
def read_health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router.router)
app.include_router(projects_router.router)
app.include_router(worklogs_router.router)
