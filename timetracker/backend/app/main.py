import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


def ensure_initial_admin_user() -> None:
    login = os.getenv("INITIAL_ADMIN_LOGIN", "admin").strip() or "admin"
    password = os.getenv("INITIAL_ADMIN_PASSWORD")

    if not password:
        return

    with SessionLocal() as session:
        existing_user = (
            session.query(models.User).filter(models.User.email == login).first()
        )

        if existing_user:
            if existing_user.role != "admin":
                existing_user.role = "admin"
                session.add(existing_user)
                session.commit()
            return

        admin_user = models.User(
            email=login,
            full_name="Administrator",
            role="admin",
            hashed_password=get_password_hash(password),
        )
        session.add(admin_user)
        session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    ensure_all_columns(engine)
    ensure_initial_admin_user()
    yield
    # Shutdown (if needed in the future)


app = FastAPI(title="Worklog API", version="2.0.0", lifespan=lifespan)

default_allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
allowed_origins = list(default_allowed_origins)
allowed_origins_env = os.getenv("CORS_ALLOW_ORIGINS")
if allowed_origins_env:
    env_origins = [
        origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()
    ]
    allowed_origins.extend(env_origins)

# Deduplicate
allowed_origins = list(set(allowed_origins))

allow_origin_regex_env = os.getenv("CORS_ALLOW_ORIGIN_REGEX")
allow_origin_regex = (
    allow_origin_regex_env.strip()
    if allow_origin_regex_env and allow_origin_regex_env.strip()
    else None
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


@app.get("/health", tags=["health"])
def read_health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router.router)
app.include_router(dictionaries_router.router)
app.include_router(projects_router.router)
app.include_router(worklogs_router.router)
app.include_router(users_router.router)
