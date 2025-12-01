# Worklog FastAPI backend

This directory contains the Python + FastAPI implementation of the Worklog backend. It exposes endpoints for authentication, project management and work log tracking.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The service listens on `http://localhost:8000` by default. Open `http://localhost:8000/docs` to explore the OpenAPI documentation.

### Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./worklog.db` | SQLAlchemy connection string. Set to the Postgres URL when running in Docker. |
| `JWT_SECRET` | `super-secret-change-me` | Secret used to sign JWT tokens. |
| `JWT_EXPIRE_MINUTES` | `1440` | Expiration time (in minutes) for generated access tokens. |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Comma separated list of origins allowed to call the API. |
| `CORS_ALLOW_ORIGIN_REGEX` | `https?://.*` | Regex used to match allowed origins; set to `None` to disable regex matching. |

### Database migrations

The application uses SQLAlchemy's metadata to create the schema automatically on startup. If you prefer Alembic migrations, the dependency is already available – run `alembic init` to bootstrap migrations.
