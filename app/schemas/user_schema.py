from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserSignupRequest(BaseModel):
    """User signup request schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    fullname: Optional[str] = None
    avatar: Optional[str] = None
    dob: Optional[datetime] = None


class UserSignupResponse(BaseModel):
    """User signup response schema."""
    email: str
    message: str = "User registered successfully. Please verify your email."


class VerifyEmailRequest(BaseModel):
    """Email verification request schema."""
    email: EmailStr
    verification_code: str = Field(..., pattern="^[0-9]{6}$", description="6-digit verification code")


class VerifyEmailResponse(BaseModel):
    """Email verification response schema."""
    message: str = "Email verified successfully"


class SignInRequest(BaseModel):
    """User sign-in request schema."""
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    """User sign-in response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    email: str


class ValidateTokenRequest(BaseModel):
    """Token validation request schema."""
    token: str


class ValidateTokenResponse(BaseModel):
    """Token validation response schema."""
    is_valid: bool
    email: Optional[str] = None
    message: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetResponse(BaseModel):
    """Password reset response schema."""
    message: str = "Password reset email sent successfully"


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    email: EmailStr
    reset_token: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class PasswordResetConfirmResponse(BaseModel):
    """Password reset confirm response schema."""
    message: str = "Password reset successfully"


class UserInfoResponse(BaseModel):
    """User info response schema."""
    email: str
    fullname: Optional[str] = None
    avatar: Optional[str] = None
    dob: Optional[datetime] = None
    is_verified: bool
    created_at: datetime
