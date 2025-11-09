from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = Field(default="user", pattern=r"^(user|admin)$")


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkLogBase(BaseModel):
    project_id: int
    date: datetime
    hours: int = Field(ge=1, le=24)
    notes: Optional[str] = Field(default=None, max_length=2000)


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(BaseModel):
    project_id: Optional[int] = None
    date: Optional[datetime] = None
    hours: Optional[int] = Field(default=None, ge=1, le=24)
    notes: Optional[str] = Field(default=None, max_length=2000)


class WorkLogRead(WorkLogBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
