"""Database schema utility helpers."""

from __future__ import annotations

import re

from sqlalchemy import Engine, inspect, text


def _slugify(value: str, *, max_length: int) -> str:
    """Create a lowercase, hyphen separated slug no longer than ``max_length``."""
    value = re.sub(r"[^\w]+", "-", value.lower()).strip("-")
    if not value:
        return ""
    if len(value) <= max_length:
        return value
    return value[:max_length].rstrip("-")


def ensure_project_code_column(engine: Engine) -> None:
    """Ensure the ``projects.code`` column exists and is populated."""
    inspector = inspect(engine)
    if "projects" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("projects")}
    if "code" in columns:
        return

    dialect = engine.dialect.name

    with engine.begin() as connection:
        column_type = "VARCHAR(50)" if dialect != "sqlite" else "TEXT"
        connection.execute(text(f"ALTER TABLE projects ADD COLUMN code {column_type}"))

        rows = connection.execute(
            text("SELECT id, name FROM projects ORDER BY id")
        ).mappings()
        existing_codes = set()
        updates: list[tuple[int, str]] = []

        for row in rows:
            base_code = _slugify(row.get("name") or "", max_length=50)
            if not base_code:
                base_code = f"project-{row['id']}"
            if len(base_code) > 50:
                base_code = base_code[:50]

            candidate = base_code
            suffix = 2
            while candidate in existing_codes:
                suffix_str = f"-{suffix}"
                candidate = base_code[: 50 - len(suffix_str)] + suffix_str
                suffix += 1
            existing_codes.add(candidate)
            updates.append((row["id"], candidate))

        for project_id, code in updates:
            connection.execute(
                text("UPDATE projects SET code = :code WHERE id = :project_id"),
                {"code": code, "project_id": project_id},
            )

        if dialect == "postgresql":
            connection.execute(text("ALTER TABLE projects ALTER COLUMN code SET NOT NULL"))
        connection.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_projects_code ON projects (code)")
        )


def ensure_worklog_site_code_column(engine: Engine) -> None:
    """Ensure the ``worklogs.site_code`` column exists and is populated."""

    inspector = inspect(engine)
    if "worklogs" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("worklogs")}
    if "site_code" in columns:
        return

    dialect = engine.dialect.name

    with engine.begin() as connection:
        column_type = "VARCHAR(50)" if dialect != "sqlite" else "TEXT"
        connection.execute(text(f"ALTER TABLE worklogs ADD COLUMN site_code {column_type}"))

        if dialect == "sqlite":
            connection.execute(
                text(
                    """
                    UPDATE worklogs
                    SET site_code = (
                        SELECT CASE
                            WHEN projects.code IS NOT NULL AND projects.code != ''
                                THEN projects.code
                            ELSE 'worklog-' || worklogs.id
                        END
                        FROM projects
                        WHERE projects.id = worklogs.project_id
                    )
                    WHERE site_code IS NULL
                    """
                )
            )
            connection.execute(
                text(
                    "UPDATE worklogs SET site_code = 'worklog-' || id "
                    "WHERE site_code IS NULL OR site_code = ''"
                )
            )
        else:
            connection.execute(
                text(
                    """
                    UPDATE worklogs
                    SET site_code = CASE
                        WHEN projects.code IS NOT NULL AND projects.code != ''
                            THEN projects.code
                        ELSE CONCAT('worklog-', worklogs.id::TEXT)
                    END
                    FROM projects
                    WHERE projects.id = worklogs.project_id
                    """
                )
            )
            connection.execute(
                text(
                    "UPDATE worklogs SET site_code = CONCAT('worklog-', id::TEXT) "
                    "WHERE site_code IS NULL OR site_code = ''"
                )
            )

        if dialect == "postgresql":
            connection.execute(text("ALTER TABLE worklogs ALTER COLUMN site_code SET NOT NULL"))


def ensure_worklog_employee_count_column(engine: Engine) -> None:
    """Ensure the ``worklogs.employee_count`` column exists and is populated."""

    inspector = inspect(engine)
    if "worklogs" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("worklogs")}
    if "employee_count" in columns:
        return

    dialect = engine.dialect.name

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE worklogs ADD COLUMN employee_count INTEGER"))
        connection.execute(
            text(
                "UPDATE worklogs SET employee_count = 1 "
                "WHERE employee_count IS NULL"
            )
        )

        if dialect == "postgresql":
            connection.execute(
                text("ALTER TABLE worklogs ALTER COLUMN employee_count SET NOT NULL")
            )


def ensure_worklog_hours_worked_column(engine: Engine) -> None:
    """Ensure the ``worklogs.hours_worked`` column exists and is populated."""

    inspector = inspect(engine)
    if "worklogs" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("worklogs")}
    if "hours_worked" in columns:
        return

    dialect = engine.dialect.name

    if dialect == "sqlite":
        column_type = "FLOAT"
    else:
        column_type = "DOUBLE PRECISION"

    with engine.begin() as connection:
        connection.execute(
            text(f"ALTER TABLE worklogs ADD COLUMN hours_worked {column_type}")
        )
        connection.execute(
            text(
                "UPDATE worklogs SET hours_worked = 8 "
                "WHERE hours_worked IS NULL"
            )
        )

        if dialect == "postgresql":
            connection.execute(
                text("ALTER TABLE worklogs ALTER COLUMN hours_worked SET NOT NULL")
            )
