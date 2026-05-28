from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterInstitutionRequest(BaseModel):
    institution_name: str = Field(min_length=2, max_length=255)
    institution_slug: str = Field(min_length=2, max_length=120, pattern=r"^[a-zA-Z0-9-]+$")
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class RegisterInstitutionData(BaseModel):
    institution_id: UUID
    user_id: UUID
    email: EmailStr
    status: str
    dev_email_verification_token: str | None = None


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32)


class LoginRequest(BaseModel):
    institution_slug: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    device_name: str | None = Field(default=None, max_length=255)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class PasswordResetRequest(BaseModel):
    institution_slug: str = Field(min_length=2, max_length=120)
    email: EmailStr


class PasswordResetRequestData(BaseModel):
    message: str
    dev_password_reset_token: str | None = None


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(min_length=32)
    new_password: str = Field(min_length=12, max_length=128)


class MessageData(BaseModel):
    message: str

