from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.user_schema import (
    UserSignupRequest,
    UserSignupResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
    SignInRequest,
    SignInResponse,
    ValidateTokenRequest,
    ValidateTokenResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirm,
    PasswordResetConfirmResponse,
    UserInfoResponse
)
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.jwt_helper import get_email_from_token, verify_token
from typing import Optional


router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# HTTPBearer security for proper Swagger UI support
bearer_scheme = HTTPBearer()


@router.post("/signup", response_model=UserSignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: UserSignupRequest):
    """
    User signup endpoint.
    
    - Accepts email, password, and optional profile info (fullname, avatar, dob)
    - Creates user in MongoDB
    - Sends verification email with 6-digit code
    """
    result = auth_service.register_user(
        request.email, 
        request.password,
        request.fullname,
        request.avatar,
        request.dob
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    # Send verification email
    verification_code = result["verification_code"]
    email_service.send_verification_email(request.email, verification_code)
    
    return UserSignupResponse(
        email=request.email,
        message="User registered successfully. Please verify your email."
    )


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(request: VerifyEmailRequest):
    """
    Verify user email.
    
    - Accepts email and verification code
    - Marks user as verified if code matches
    """
    result = auth_service.verify_email(request.email, request.verification_code)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return VerifyEmailResponse(message="Email verified successfully")


@router.post("/signin", response_model=SignInResponse)
async def signin(request: SignInRequest):
    """
    User sign-in endpoint.
    
    - Accepts email and password
    - Returns JWT access token if credentials are valid
    - Requires verified email
    """
    result = auth_service.authenticate_user(request.email, request.password)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )
    
    return SignInResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"],
        email=result["email"]
    )


@router.post("/validate-token", response_model=ValidateTokenResponse)
async def validate_token(request: ValidateTokenRequest):
    """
    Validate JWT access token.
    
    - Accepts JWT token
    - Returns validation status and email if valid
    """
    payload = verify_token(request.token)
    
    if not payload:
        return ValidateTokenResponse(
            is_valid=False,
            message="Invalid or expired token"
        )
    
    email = payload.get("sub")
    return ValidateTokenResponse(
        is_valid=True,
        email=email,
        message="Token is valid"
    )


@router.post("/password-reset", response_model=PasswordResetResponse)
async def password_reset(request: PasswordResetRequest):
    """
    Initiate password reset.
    
    - Accepts user email
    - Sends password reset email with token
    """
    result = auth_service.initiate_password_reset(request.email)
    
    if result["success"]:
        # Send password reset email
        reset_token = result.get("reset_token")
        if reset_token:
            email_service.send_password_reset_email(request.email, reset_token)
    
    # Always return success for security (don't reveal if user exists)
    return PasswordResetResponse(
        message="Password reset email sent successfully"
    )


@router.post("/password-reset-confirm", response_model=PasswordResetConfirmResponse)
async def password_reset_confirm(request: PasswordResetConfirm):
    """
    Confirm password reset.
    
    - Accepts email, reset token, and new password
    - Updates password in database
    """
    result = auth_service.confirm_password_reset(
        request.email,
        request.reset_token,
        request.new_password
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return PasswordResetConfirmResponse(message="Password reset successfully")


@router.get("/test-token")
async def test_token(x_auth_token: str = Header(None)):
    """
    Test endpoint to verify token is being sent correctly.
    Uses X-Auth-Token header for testing.
    """
    if not x_auth_token:
        return {
            "message": "No X-Auth-Token header received",
            "x_auth_token": None
        }
    
    return {
        "message": "Token received successfully",
        "x_auth_token": x_auth_token,
        "token_length": len(x_auth_token)
    }


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user(token: str = Header(...)):
    """
    Get current authenticated user info.
    
    - Requires valid JWT token in Token header
    """
    email = get_email_from_token(token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = auth_service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserInfoResponse(
        email=user["email"],
        fullname=user.get("fullname"),
        avatar=user.get("avatar"),
        dob=user.get("dob"),
        is_verified=user.get("is_verified", False),
        created_at=user.get("created_at")
    )

