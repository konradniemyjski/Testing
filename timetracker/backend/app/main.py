"""Fixed main.py with complete initialization."""

from __future__ import annotations

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Import models to register SQLAlchemy mappings before table creation
from . import models  # noqa: F401
from .db import Base, SessionLocal, engine
from .schema_utils import ensure_all_columns
from .auth import get_password_hash
from .routers import auth as auth_router
from .routers import dictionaries as dictionaries_router
from .routers import projects as projects_router
from .routers import worklogs as worklogs_router
from .routers import users as users_router
from .routers import reports as reports_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_initial_admin_user() -> None:
    """Create initial admin user if configured via environment variables."""
    login = os.getenv("INITIAL_ADMIN_LOGIN", "admin").strip() or "admin"
    password = os.getenv("INITIAL_ADMIN_PASSWORD")

    if not password:
        logger.info("INITIAL_ADMIN_PASSWORD not set, skipping admin user creation")
        return

    with SessionLocal() as session:
        existing_user = (
            session.query(models.User).filter(models.User.email == login).first()
        )

        if existing_user:
            if existing_user.role != "admin":
                logger.info(f"Updating {login} to admin role")
                existing_user.role = "admin"
                session.add(existing_user)
                session.commit()
            else:
                logger.info(f"Admin user {login} already exists")
            return

        logger.info(f"Creating initial admin user: {login}")
        admin_user = models.User(
            email=login,
            full_name="Administrator",
            role="admin",
            hashed_password=get_password_hash(password),
        )
        session.add(admin_user)
        session.commit()
        logger.info(f"Admin user {login} created successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown."""
    # Startup
    logger.info("Starting up FastAPI application...")
    Base.metadata.create_all(bind=engine)
    ensure_all_columns(engine)
    ensure_initial_admin_user()
    logger.info("Startup complete")

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Worklog API",
    version="2.0.0",
    description="API for managing work logs, projects, and teams",
    lifespan=lifespan,
)

# ===== CORS Configuration =====

default_allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://localhost",
    "https://localhost:3000",
    "https://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://127.0.0.1",
    "https://127.0.0.1:3000",
    "https://127.0.0.1:5173",
]


def deduplicate_preserve_order(values: list[str]) -> list[str]:
    # dict preserves insertion order since Python 3.7
    return list(dict.fromkeys(values))




allowed_origins = list(default_allowed_origins)

# Add origins from environment variable
allowed_origins_env = os.getenv("CORS_ALLOW_ORIGINS")
if allowed_origins_env:
    env_origins = [
        origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()
    ]
    allowed_origins.extend(env_origins)

# Deduplicate while preserving preference order
allowed_origins = deduplicate_preserve_order(allowed_origins)

# Get regex pattern if specified
allow_origin_regex_env = os.getenv("CORS_ALLOW_ORIGIN_REGEX")
allow_origin_regex = (
    allow_origin_regex_env.strip()
    if allow_origin_regex_env and allow_origin_regex_env.strip()
    else None
)

# Don't mix wildcard with regex
if allowed_origins == ["*"]:
    allow_origin_regex = None

logger.info(f"CORS allowed origins: {allowed_origins}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
trusted_hosts = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1")
if trusted_hosts:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts.split(","),
    )


# ===== Health Check Route =====

@app.get("/health", tags=["health"])
def read_health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/", tags=["info"])
def read_root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "name": "Worklog API",
        "version": "2.0.0",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
    }


# ===== Include Routers =====

app.include_router(auth_router.router)
app.include_router(dictionaries_router.router)
app.include_router(projects_router.router)
app.include_router(worklogs_router.router)
app.include_router(users_router.router)
app.include_router(reports_router.router)

logger.info("All routers included successfully")
