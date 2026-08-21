from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(char.isupper() for char in value) or not any(char.islower() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("password must include upper, lower, and numeric characters")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=255)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=64)
    phone: str | None = Field(default=None, max_length=32)
    city: str | None = Field(default=None, max_length=128)
    state: str | None = Field(default=None, max_length=128)
    country: str | None = Field(default=None, max_length=128)
    education_level: str | None = Field(default=None, max_length=128)
    institution: str | None = Field(default=None, max_length=255)
    degree: str | None = Field(default=None, max_length=255)
    stream: str | None = Field(default=None, max_length=255)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    exam_interests: list[str] | None = Field(default=None, max_length=20)
    opportunity_interests: list[str] | None = Field(default=None, max_length=20)
    preferred_locations: list[str] | None = Field(default=None, max_length=20)
    remote_preference: bool | None = None
    career_interests: list[str] | None = Field(default=None, max_length=20)
    target_roles: list[str] | None = Field(default=None, max_length=20)
    skills: list[str] | None = Field(default=None, max_length=30)
    experience_level: str | None = Field(default=None, max_length=64)
    notification_preferences: dict[str, bool] | None = None


class ProfileResponse(ProfileUpdate):
    id: str
    user_id: str
    goal: str | None = None
    bio: str | None = None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: Literal["student", "admin", "super_admin"]
    email_verified: bool
    profile: ProfileResponse | None = None

    model_config = {"from_attributes": True}


class TokenRequest(BaseModel):
    token: str = Field(min_length=1, max_length=512)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=1, max_length=512)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return RegisterRequest(name="valid", email="valid@example.com", password=value).password
