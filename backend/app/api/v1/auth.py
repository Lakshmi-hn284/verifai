"""
VERIFAI - Authentication API Router
Handles User Registration, Login, Token Refresh, and Session Invalidation.
"""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.audit import log_security_event
from app.core.errors import AuthenticationError, VerifaiException
from app.domain.models import User
from app.domain.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    ApiResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def register(
    req_data: UserRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account with Argon2id password hashing."""
    # Check if email is already taken
    existing = await db.execute(select(User).where(User.email == req_data.email.lower()))
    if existing.scalar_one_or_none():
        raise VerifaiException(
            message="An account with this email address already exists",
            code="EMAIL_ALREADY_EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Hash password with Argon2id
    hashed = hash_password(req_data.password)

    new_user = User(
        email=req_data.email.lower(),
        hashed_password=hashed,
        full_name=req_data.full_name,
        is_active=True,
        is_verified=False
    )
    db.add(new_user)
    await db.flush()

    # Create tokens
    token_payload = {"sub": new_user.id, "email": new_user.email}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    # Audit log
    await log_security_event(
        db=db,
        event_type="USER_REGISTER",
        status="SUCCESS",
        user_id=new_user.id,
        ip_address=request.client.host if request.client else None,
        details={"email": new_user.email, "full_name": new_user.full_name}
    )

    token_data = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        user=UserResponse.model_validate(new_user)
    )

    return ApiResponse(
        success=True,
        data=token_data.model_dump()
    )


@router.post("/login", response_model=ApiResponse)
async def login(
    req_data: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user with email and password."""
    client_ip = request.client.host if request.client else None
    
    result = await db.execute(select(User).where(User.email == req_data.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req_data.password, user.hashed_password):
        if user:
            await log_security_event(
                db=db,
                event_type="USER_LOGIN_FAILED",
                status="FAILURE",
                user_id=user.id,
                ip_address=client_ip,
                details={"reason": "Invalid password"}
            )
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    # Generate JWT tokens
    token_payload = {"sub": user.id, "email": user.email}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    # Audit log
    await log_security_event(
        db=db,
        event_type="USER_LOGIN",
        status="SUCCESS",
        user_id=user.id,
        ip_address=client_ip,
        details={"email": user.email}
    )

    token_data = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        user=UserResponse.model_validate(user)
    )

    return ApiResponse(
        success=True,
        data=token_data.model_dump()
    )


@router.post("/refresh", response_model=ApiResponse)
async def refresh_access_token(
    req_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Issue a new access token using a valid refresh token."""
    payload = decode_token(req_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthenticationError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthenticationError("User no longer exists or is inactive")

    new_payload = {"sub": user.id, "email": user.email}
    new_access_token = create_access_token(new_payload)

    return ApiResponse(
        success=True,
        data={
            "access_token": new_access_token,
            "token_type": "Bearer"
        }
    )


@router.post("/logout", response_model=ApiResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log out user and record security audit trail."""
    await log_security_event(
        db=db,
        event_type="USER_LOGOUT",
        status="SUCCESS",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )

    return ApiResponse(
        success=True,
        data={"message": "Successfully logged out"}
    )
