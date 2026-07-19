"""User and authentication response contracts."""

from pydantic import BaseModel, EmailStr, Field


class CurrentUser(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
