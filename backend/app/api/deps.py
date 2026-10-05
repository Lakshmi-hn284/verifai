"""
VERIFAI - API Dependencies
Provides dependency injection for Database Sessions and Authenticated Current User.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import decode_token
from app.core.errors import AuthenticationError, AuthorizationError
from app.db.session import get_db
from app.domain.models import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validate bearer token and return authenticated User entity."""
    if not token:
        raise AuthenticationError("Authorization token required")

    payload = decode_token(token)
    if not payload:
        raise AuthenticationError("Invalid or expired authentication token")

    token_type = payload.get("type")
    if token_type != "access":
        raise AuthenticationError("Invalid token type: expected access token")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token missing subject identifier")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User associated with token no longer exists")

    if not user.is_active:
        raise AuthorizationError("User account has been deactivated")

    return user
