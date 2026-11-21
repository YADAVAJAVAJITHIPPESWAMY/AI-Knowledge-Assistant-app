"""
Authentication API Endpoints
Register, Login, Refresh, Logout, Profile update, Password change, and Account deletion.
Supports both HttpOnly secure cookies and Bearer tokens for flexibility.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate, UserPasswordUpdate
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, response: Response, db: Session = Depends(get_db)):
    """Registers a new user and issues access/refresh tokens with HttpOnly cookies."""
    # Check if email is already taken
    existing_user = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing_user:
        raise BadRequestException("An account with this email address already exists.")

    # Hash password with Argon2
    hashed_pw = hash_password(user_in.password)
    user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=hashed_pw
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Issue tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    # Set secure HttpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.is_production
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
        secure=settings.is_production
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticates user with email and password."""
    user = db.query(User).filter(User.email == login_data.email.lower().strip()).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise UnauthorizedException("Incorrect email or password.")

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.is_production
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
        secure=settings.is_production
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user)
    )


@router.post("/logout")
def logout(response: Response):
    """Logs out user and clears authentication cookies."""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(
    request: Request,
    response: Response,
    payload: Optional[RefreshTokenRequest] = None,
    db: Session = Depends(get_db)
):
    """Refreshes the session access token."""
    token = None
    if payload and payload.refresh_token:
        token = payload.refresh_token
    else:
        token = request.cookies.get("refresh_token")

    if not token:
        raise UnauthorizedException("Refresh token missing.")

    decoded = decode_token(token)
    if not decoded or decoded.get("type") != "refresh":
        raise UnauthorizedException("Invalid or expired refresh token.")

    user_id_str = decoded.get("sub")
    user = db.query(User).filter(User.id == user_id_str).first()
    if not user:
        raise UnauthorizedException("User not found.")

    new_access_token = create_access_token(subject=str(user.id))
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.is_production
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user)
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently logged-in user profile."""
    return UserOut.model_validate(current_user)


@router.put("/profile", response_model=UserOut)
def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates user profile details."""
    if user_in.name:
        current_user.name = user_in.name.strip()
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)


@router.post("/change-password")
def change_password(
    pwd_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Securely updates the user's password."""
    if not verify_password(pwd_data.current_password, current_user.password_hash):
        raise BadRequestException("Current password is incorrect.")

    current_user.password_hash = hash_password(pwd_data.new_password)
    db.commit()
    return {"message": "Password successfully updated"}


@router.delete("/account")
def delete_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently deletes the user account, documents, embeddings, and chat history."""
    db.delete(current_user)
    db.commit()
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "User account and all associated data have been permanently deleted."}
