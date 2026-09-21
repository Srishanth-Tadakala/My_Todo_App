"""
Authentication Router
"""

from fastapi import APIRouter, Depends, Header
from app.core.rate_limit import rate_limit_auth
from app.core.responses import success_response
from app.core.security import CurrentUser, parse_bearer_token
from app.dependencies import get_current_user
from app.schemas.auth import LoginRequest, SignUpRequest, TokenResponse, UserResponse
from app.services.auth_service import auth_service
from app.services.user_service import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=201, dependencies=[Depends(rate_limit_auth)])
async def sign_up(req: SignUpRequest):
    """Registers a new user via Supabase Auth and initializes profile."""
    return await auth_service.sign_up(req)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit_auth)])
async def login(req: LoginRequest):
    """Authenticates user credentials and returns session tokens."""
    return await auth_service.login(req)


@router.post("/logout", status_code=200)
async def logout(authorization: str = Header(..., alias="Authorization")):
    """Signs out user and invalidates session token."""
    token = parse_bearer_token(authorization)
    await auth_service.logout(token)
    return success_response({"message": "Successfully logged out."})


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Returns the authenticated user's profile information."""
    prof = await user_service.get_profile(current_user.id)
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=prof.full_name,
        avatar_url=prof.avatar_url,
        timezone=prof.timezone,
    )
