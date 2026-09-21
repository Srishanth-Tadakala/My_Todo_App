"""
Authentication Service
Integrates with Supabase Auth authority or mock test environment.
"""

from typing import Any, Dict, Optional
import uuid
from app.config import get_settings
from app.core.exceptions import ConflictException, UnauthorizedException, ValidationException
from app.core.logging import logger
from app.database.repositories import user_repo
from app.database.supabase import get_supabase_anon_client
from app.schemas.auth import LoginRequest, SignUpRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, u_repo=None):
        self.user_repo = u_repo or user_repo

    async def sign_up(self, req: SignUpRequest) -> TokenResponse:
        settings = get_settings()

        # In testing or mock mode
        if settings.is_testing or "dummy" in settings.SUPABASE_ANON_KEY:
            user_id = str(uuid.uuid4())
            profile_data = {
                "id": user_id,
                "full_name": req.full_name or req.email.split("@")[0],
                "avatar_url": None,
                "timezone": req.timezone or "UTC",
            }
            await self.user_repo.update_profile(user_id, profile_data)
            await self.user_repo.update_settings(user_id, {"timezone": req.timezone or "UTC"})

            user_res = UserResponse(
                id=user_id,
                email=req.email,
                full_name=profile_data["full_name"],
                timezone=profile_data["timezone"],
            )
            return TokenResponse(
                access_token=f"test-token-{user_id}",
                token_type="bearer",
                expires_in=3600,
                refresh_token=f"test-refresh-{user_id}",
                user=user_res,
            )

        # Real Supabase Auth
        try:
            client = get_supabase_anon_client()
            res = client.auth.sign_up({"email": req.email, "password": req.password})
            if not res.user:
                raise ValidationException("Failed to register user.")

            user_id = str(res.user.id)
            profile_data = {
                "id": user_id,
                "full_name": req.full_name or req.email.split("@")[0],
                "timezone": req.timezone or "UTC",
            }
            await self.user_repo.update_profile(user_id, profile_data)
            await self.user_repo.update_settings(user_id, {"timezone": req.timezone or "UTC"})

            access_token = res.session.access_token if res.session else f"token-{user_id}"
            refresh_token = res.session.refresh_token if res.session else None

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=3600,
                refresh_token=refresh_token,
                user=UserResponse(
                    id=user_id,
                    email=req.email,
                    full_name=profile_data["full_name"],
                    timezone=profile_data["timezone"],
                ),
            )
        except Exception as e:
            logger.error(f"Sign up error: {e}")
            raise ValidationException(f"Registration failed: {str(e)}")

    async def login(self, req: LoginRequest) -> TokenResponse:
        settings = get_settings()

        if settings.is_testing or "dummy" in settings.SUPABASE_ANON_KEY:
            user_id = "00000000-0000-0000-0000-000000000001"
            prof = await self.user_repo.get_profile(user_id)
            if not prof:
                prof = await self.user_repo.update_profile(
                    user_id,
                    {"full_name": "Demo User", "timezone": "UTC"},
                )
            return TokenResponse(
                access_token=f"test-token-{user_id}",
                token_type="bearer",
                expires_in=3600,
                refresh_token=f"test-refresh-{user_id}",
                user=UserResponse(
                    id=user_id,
                    email=req.email,
                    full_name=prof.get("full_name", "Demo User"),
                    timezone=prof.get("timezone", "UTC"),
                ),
            )

        try:
            client = get_supabase_anon_client()
            res = client.auth.sign_in_with_password({"email": req.email, "password": req.password})
            if not res.user or not res.session:
                raise UnauthorizedException("Invalid credentials.")

            user_id = str(res.user.id)
            prof = await self.user_repo.get_profile(user_id) or {}
            return TokenResponse(
                access_token=res.session.access_token,
                token_type="bearer",
                expires_in=res.session.expires_in or 3600,
                refresh_token=res.session.refresh_token,
                user=UserResponse(
                    id=user_id,
                    email=res.user.email,
                    full_name=prof.get("full_name"),
                    avatar_url=prof.get("avatar_url"),
                    timezone=prof.get("timezone", "UTC"),
                ),
            )
        except UnauthorizedException:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise UnauthorizedException("Invalid email or password.")

    async def logout(self, token: str):
        settings = get_settings()
        if settings.is_testing or "dummy" in settings.SUPABASE_ANON_KEY:
            return True
        try:
            client = get_supabase_anon_client()
            client.auth.sign_out()
            return True
        except Exception as e:
            logger.warning(f"Logout error: {e}")
            return True


auth_service = AuthService()
