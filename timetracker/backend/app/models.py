from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)

    worklogs: Mapped[list["WorkLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    worklogs: Mapped[list["WorkLog"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class WorkLog(Base, TimestampMixin):
    __tablename__ = "worklogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    team_member_id: Mapped[int | None] = mapped_column(
        ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True
    )
    accommodation_company_id: Mapped[int | None] = mapped_column(
        ForeignKey("accommodation_companies.id", ondelete="SET NULL"), nullable=True
    )
    catering_company_id: Mapped[int | None] = mapped_column(
        ForeignKey("catering_companies.id", ondelete="SET NULL"), nullable=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    site_code: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_count: Mapped[int] = mapped_column(Integer, nullable=False)
    hours_worked: Mapped[float] = mapped_column(Float, nullable=False)
    meals_served: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overnight_stays: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    absences: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship(back_populates="worklogs")
    project: Mapped[Project] = relationship(back_populates="worklogs")
<<<<<<< HEAD
=======
<<<<<<< ours
    team_member: Mapped["TeamMember" | None] = relationship(back_populates="worklogs")
    accommodation_company: Mapped["AccommodationCompany" | None] = relationship(
        back_populates="worklogs"
    )
    catering_company: Mapped["CateringCompany" | None] = relationship(back_populates="worklogs")
=======
>>>>>>> master
    team_member: Mapped[TeamMember | None] = relationship(back_populates="worklogs")
    accommodation_company: Mapped[AccommodationCompany | None] = relationship(
        back_populates="worklogs"
    )
    catering_company: Mapped[CateringCompany | None] = relationship(back_populates="worklogs")
<<<<<<< HEAD
=======
>>>>>>> theirs
>>>>>>> master


class CateringCompany(Base, TimestampMixin):
    __tablename__ = "catering_companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tax_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    worklogs: Mapped[list[WorkLog]] = relationship(back_populates="catering_company")


class AccommodationCompany(Base, TimestampMixin):
    __tablename__ = "accommodation_companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tax_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    worklogs: Mapped[list[WorkLog]] = relationship(back_populates="accommodation_company")


class TeamMember(Base, TimestampMixin):
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    worklogs: Mapped[list[WorkLog]] = relationship(back_populates="team_member")
