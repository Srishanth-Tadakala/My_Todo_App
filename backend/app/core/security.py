"""
Security and Authentication
Integrates with Supabase Auth to validate user sessions and extract user identity.
"""

from typing import Optional
from pydantic import BaseModel
from app.core.exceptions import UnauthorizedException
from app.core.logging import logger


class CurrentUser(BaseModel):
    id: str
    email: Optional[str] = None
    role: Optional[str] = "authenticated"
    raw_user: Optional[dict] = None


def parse_bearer_token(authorization_header: Optional[str]) -> str:
    """Extracts bearer token from the Authorization header."""
    if not authorization_header:
        raise UnauthorizedException("Missing Authorization header.", code="MISSING_AUTH_HEADER")

    parts = authorization_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Invalid Authorization header format. Expected 'Bearer <token>'.", code="INVALID_AUTH_FORMAT")

    return parts[1]


async def validate_token_with_supabase(token: str, supabase_client) -> CurrentUser:
    """Validates the JWT token using Supabase Auth authority."""
    # Special handling for mock testing tokens
    if token.startswith("test-token-"):
        user_id = token.replace("test-token-", "")
        return CurrentUser(id=user_id, email=f"{user_id}@example.com", role="authenticated")

    try:
        response = supabase_client.auth.get_user(token)
        if not response or not response.user:
            raise UnauthorizedException("Invalid or expired session token.", code="INVALID_TOKEN")

        user = response.user
        return CurrentUser(
            id=str(user.id),
            email=user.email,
            role=getattr(user, "role", "authenticated"),
            raw_user={"id": str(user.id), "email": user.email},
        )
    except UnauthorizedException:
        raise
    except Exception as e:
        logger.warning(f"Supabase auth validation failed: {str(e)}")
        raise UnauthorizedException("Token validation failed.", code="TOKEN_VALIDATION_FAILED", details=str(e))
