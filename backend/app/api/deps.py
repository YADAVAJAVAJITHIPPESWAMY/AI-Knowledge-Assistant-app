"""
API Dependencies
Provides database session, current authenticated user extraction, and token validation.
"""
from typing import Generator, Optional
import uuid
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.db.session import get_db
from app.models.user import User

# Optional oauth2 scheme for OpenAPI UI documentation
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def get_current_user(
    request: Request,
    token_from_header: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts the authenticated user from either Authorization header Bearer token
    or secure HttpOnly 'access_token' cookie.
    """
    token = token_from_header
    if not token:
        # Check cookie
        token = request.cookies.get("access_token")

    if not token:
        raise UnauthorizedException("Authentication credentials were not provided.")

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired session token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Malformed token payload.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user ID in token.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("User not found.")

    return user
