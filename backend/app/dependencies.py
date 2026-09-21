"""
FastAPI Request Dependencies
Handles authentication, user extraction, and idempotency keys.
"""

from typing import Optional
from fastapi import Depends, Header, Request
from app.core.exceptions import UnauthorizedException
from app.core.security import CurrentUser, parse_bearer_token, validate_token_with_supabase
from app.database.supabase import get_supabase_anon_client, get_user_scoped_client


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> CurrentUser:
    """Dependency validating bearer token and returning the authenticated CurrentUser."""
    token = parse_bearer_token(authorization)
    client = get_supabase_anon_client()
    return await validate_token_with_supabase(token, client)


async def get_current_user_id(
    current_user: CurrentUser = Depends(get_current_user),
) -> str:
    """Convenience dependency returning the authenticated user_id string."""
    return current_user.id


def get_idempotency_key(
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> Optional[str]:
    """Extracts optional Idempotency-Key header for duplicate request protection."""
    return idempotency_key


async def get_user_client(
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """Returns a Supabase client scoped with user's access token for RLS enforcement."""
    token = parse_bearer_token(authorization)
    return get_user_scoped_client(token)
