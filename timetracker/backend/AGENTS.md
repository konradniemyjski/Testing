# Agent Instructions (backend)

- Keep FastAPI endpoints organized under `app/routers` and shared schemas in `app/schemas.py`; models live in `app/models.py`.
- Use SQLAlchemy `Mapped[...]` annotations with forward references for relationships when needed; avoid string unions that break evaluation.
- Maintain typing and validation with Pydantic models and keep environment variable defaults aligned with `backend/README.md`.
- Prefer lightweight checks (import/startup) over adding new dependencies unless required by the feature.
