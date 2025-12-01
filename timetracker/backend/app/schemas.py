from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints


LoginIdentifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None


class UserBase(BaseModel):
    email: LoginIdentifier
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: str = Field(default="user", pattern=r"^(user|admin)$")


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: str = Field(pattern=r"^(user|admin)$")


class UserUpdate(BaseModel):
    email: Optional[LoginIdentifier] = None
    full_name: Optional[str | None] = Field(default=None, max_length=255)


class UserSelfUpdate(BaseModel):
    email: Optional[LoginIdentifier] = None
    full_name: Optional[str | None] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=6)
    current_password: Optional[str] = Field(default=None, min_length=6)


class UserSummary(BaseModel):
    id: int
    email: LoginIdentifier
    full_name: Optional[str | None] = Field(default=None, max_length=255)

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


NIP_PATTERN = r"^((\d{3}[- ]\d{3}[- ]\d{2}[- ]\d{2})|(\d{3}[- ]\d{2}[- ]\d{2}[- ]\d{3}))$"


class CateringCompanyBase(BaseModel):
    tax_id: str = Field(min_length=1, max_length=64, pattern=NIP_PATTERN)
    name: str = Field(min_length=1, max_length=255)


class CateringCompanyCreate(CateringCompanyBase):
    pass


class CateringCompanyRead(CateringCompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccommodationCompanyBase(BaseModel):
    tax_id: str = Field(min_length=1, max_length=64, pattern=NIP_PATTERN)
    name: str = Field(min_length=1, max_length=255)


class AccommodationCompanyCreate(AccommodationCompanyBase):
    pass


class AccommodationCompanyRead(AccommodationCompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberRead(TeamMemberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkLogBase(BaseModel):
    project_id: int
    team_member_id: int | None = None
    accommodation_company_id: int | None = None
    catering_company_id: int | None = None
    date: datetime
    site_code: str = Field(min_length=1, max_length=50)
    employee_count: int = Field(ge=1, le=1000)
    hours_worked: float = Field(gt=0, le=2000)
    meals_served: int = Field(default=0, ge=0, le=2000)
    overnight_stays: int = Field(default=0, ge=0, le=2000)
    absences: int = Field(default=0, ge=0, le=2000)
    notes: Optional[str] = Field(default=None, max_length=2000)


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(BaseModel):
    project_id: Optional[int] = None
    date: Optional[datetime] = None
    site_code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    employee_count: Optional[int] = Field(default=None, ge=1, le=1000)
    hours_worked: Optional[float] = Field(default=None, gt=0, le=2000)
    meals_served: Optional[int] = Field(default=None, ge=0, le=2000)
    overnight_stays: Optional[int] = Field(default=None, ge=0, le=2000)
    absences: Optional[int] = Field(default=None, ge=0, le=2000)
    notes: Optional[str] = Field(default=None, max_length=2000)
    team_member_id: Optional[int] = None
    accommodation_company_id: Optional[int] = None
    catering_company_id: Optional[int] = None


class WorkLogRead(WorkLogBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserSummary] = None
    team_member: Optional[TeamMemberRead] = None
    accommodation_company: Optional[AccommodationCompanyRead] = None
    catering_company: Optional[CateringCompanyRead] = None

    class Config:
        from_attributes = True
