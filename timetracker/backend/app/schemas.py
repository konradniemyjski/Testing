"""Fixed and improved schemas with Pydantic v2 compatibility."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Optional, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator


# Custom type for email/login identifiers
LoginIdentifier = Annotated[str, Field(min_length=1, max_length=255)]

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


# ===== Authentication Schemas =====

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    sub: Optional[str] = None


# ===== User Schemas =====

class UserBase(BaseModel):
    """Base user schema."""
    email: LoginIdentifier
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: str = Field(default="user", pattern=r"^(user|admin)$")


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(min_length=6, max_length=255)


class UserRead(UserBase):
    """User read schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    """Update user role."""
    role: str = Field(pattern=r"^(user|admin)$")


class UserUpdate(BaseModel):
    """Update user profile (admin)."""
    email: Optional[LoginIdentifier] = None
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserSelfUpdate(BaseModel):
    """Update own profile (user)."""
    email: Optional[LoginIdentifier] = None
    full_name: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=6, max_length=255)
    current_password: Optional[str] = Field(default=None, min_length=6, max_length=255)

    @field_validator('password')
    @classmethod
    def password_requires_current(cls, v, info):
        """Validate that current_password is provided when changing password."""
        if v is not None and info.data.get('current_password') is None:
            raise ValueError('current_password required when changing password')
        return v


class UserSummary(BaseModel):
    """Summary of user (for relationships)."""
    id: int
    email: LoginIdentifier
    full_name: Optional[str] = Field(default=None, max_length=255)

    model_config = {"from_attributes": True}


# ===== Project Schemas =====

class ProjectBase(BaseModel):
    """Base project schema."""
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectCreate(ProjectBase):
    """Create project."""
    pass


class ProjectUpdate(BaseModel):
    """Update project."""
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectRead(ProjectBase):
    """Read project."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Company Schemas =====

# Polish tax ID (NIP) pattern: XXX-XXX-XX-XX or XXX-XX-XX-XXX
NIP_PATTERN = r"^((\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})|(\d{3}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{3}))$"


class CateringCompanyBase(BaseModel):
    """Base catering company schema."""
    tax_id: str = Field(min_length=1, max_length=64, pattern=NIP_PATTERN)
    name: str = Field(min_length=1, max_length=255)


class CateringCompanyCreate(CateringCompanyBase):
    """Create catering company."""
    pass


class CateringCompanyUpdate(CateringCompanyBase):
    """Update catering company."""
    pass


class CateringCompanyRead(CateringCompanyBase):
    """Read catering company."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccommodationCompanyBase(BaseModel):
    """Base accommodation company schema."""
    tax_id: str = Field(min_length=1, max_length=64, pattern=NIP_PATTERN)
    name: str = Field(min_length=1, max_length=255)


class AccommodationCompanyCreate(AccommodationCompanyBase):
    """Create accommodation company."""
    pass


class AccommodationCompanyUpdate(AccommodationCompanyBase):
    """Update accommodation company."""
    pass


class AccommodationCompanyRead(AccommodationCompanyBase):
    """Read accommodation company."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Team Schemas =====

class TeamMemberRole(str, Enum):
    """Team member roles (Polish)."""
    worker = "Pracownik"
    foreman = "Brygadzista"


class TeamMemberBase(BaseModel):
    """Base team member schema."""
    name: str = Field(min_length=1, max_length=255)
    role: TeamMemberRole = Field(default=TeamMemberRole.worker)
    team_id: Optional[int] = Field(default=None)


class TeamMemberCreate(TeamMemberBase):
    """Create team member."""
    pass


class TeamMemberUpdate(TeamMemberBase):
    """Update team member."""
    pass


class TeamMemberRead(TeamMemberBase):
    """Read team member."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TeamBase(BaseModel):
    """Base team schema."""
    name: str = Field(min_length=1, max_length=255)


class TeamCreate(TeamBase):
    """Create team."""
    pass


class TeamUpdate(TeamBase):
    """Update team."""
    pass


class TeamRead(TeamBase):
    """Read team with members."""
    id: int
    members: list[TeamMemberRead]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== WorkLog Schemas =====

class WorkLogBase(BaseModel):
    """Base worklog schema."""
    project_id: int
    team_member_id: Optional[int] = None
    accommodation_company_id: Optional[int] = None
    catering_company_id: Optional[int] = None
    date: datetime
    site_code: str = Field(min_length=1, max_length=50)
    employee_count: int = Field(ge=1, le=1000)
    hours_worked: float = Field(ge=0, le=2000)
    meals_served: int = Field(default=0, ge=0, le=2000)
    overnight_stays: int = Field(default=0, ge=0, le=2000)
    absences: int = Field(default=0, ge=0, le=2000)
    notes: Optional[str] = Field(default=None, max_length=2000)


class WorkLogCreate(WorkLogBase):
    """Create worklog."""
    pass


class WorkLogUpdate(BaseModel):
    """Update worklog."""
    project_id: Optional[int] = None
    date: Optional[datetime] = None
    site_code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    employee_count: Optional[int] = Field(default=None, ge=1, le=1000)
    hours_worked: Optional[float] = Field(default=None, ge=0, le=2000)
    meals_served: Optional[int] = Field(default=None, ge=0, le=2000)
    overnight_stays: Optional[int] = Field(default=None, ge=0, le=2000)
    absences: Optional[int] = Field(default=None, ge=0, le=2000)
    notes: Optional[str] = Field(default=None, max_length=2000)
    team_member_id: Optional[int] = None
    accommodation_company_id: Optional[int] = None
    catering_company_id: Optional[int] = None


class WorkLogRead(WorkLogBase):
    """Read worklog."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserSummary] = None
    team_member: Optional[TeamMemberRead] = None
    accommodation_company: Optional[AccommodationCompanyRead] = None
    catering_company: Optional[CateringCompanyRead] = None

    model_config = {"from_attributes": True}
