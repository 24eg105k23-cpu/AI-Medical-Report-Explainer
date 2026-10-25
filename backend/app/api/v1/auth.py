from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_token_from_header
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    revoke_token,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user account with secure password hashing.
    """
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    hashed_pw = hash_password(request.password)
    user = User(
        email=request.email,
        password_hash=hashed_pw,
        account_status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    AuditService.record_event(
        db=db,
        event_type="user_registered",
        user_id=user.id,
        metadata={"email": user.email},
    )

    return APIResponse(
        success=True,
        message="User registered successfully.",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="User login and token generation",
)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user credentials and issue a signed JWT access token.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive or suspended.",
        )

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=user.id, expires_delta=expires_delta)

    AuditService.record_event(
        db=db,
        event_type="user_login",
        user_id=user.id,
        metadata={"email": user.email},
    )

    return APIResponse(
        success=True,
        message="Login successful.",
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return currently authenticated user information.
    """
    return APIResponse(
        success=True,
        message="Current user fetched successfully.",
        data=UserResponse.model_validate(current_user),
    )


@router.post(
    "/logout",
    response_model=APIResponse[None],
    summary="Log out and invalidate current token",
)
def logout(
    token: str = Depends(get_token_from_header),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Invalidate the current JWT token in the token blacklist.
    """
    revoke_token(token)
    AuditService.record_event(
        db=db,
        event_type="user_logout",
        user_id=current_user.id,
    )
    return APIResponse(
        success=True,
        message="Logged out successfully. Token has been invalidated.",
        data=None,
    )
