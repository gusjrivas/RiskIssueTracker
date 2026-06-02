import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.schemas.common import UserRole, UserStatus, UserTheme


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    picture: str | None = None
    role: UserRole
    status: UserStatus
    theme: UserTheme = UserTheme.light
    has_password: bool = False
    created_at: datetime


class UserAdminUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class UpdateThemeRequest(BaseModel):
    theme: UserTheme


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
