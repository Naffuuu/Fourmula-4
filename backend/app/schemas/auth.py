from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.student
    roll_number: str | None = Field(default=None, max_length=64)

    @field_validator("roll_number")
    @classmethod
    def roll_number_required_for_students(cls, value, info):
        role = info.data.get("role")
        if role == UserRole.student and not value:
            raise ValueError("roll_number is required for students")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class OAuthLoginRequest(BaseModel):
    # Google: ID token (JWT) from Google Identity Services.
    # Facebook: short-lived user access token from the Facebook JS SDK.
    credential: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    role: UserRole
    avatar_url: str | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
