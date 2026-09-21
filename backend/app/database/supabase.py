"""
Supabase Client Management
Provides both User-Scoped and Service-Role Supabase clients.
"""

from typing import Optional
from supabase import create_client, Client
from app.config import get_settings
from app.core.logging import logger

_anon_client: Optional[Client] = None
_service_client: Optional[Client] = None


def get_supabase_anon_client() -> Client:
    """Returns singleton Supabase client using anon key."""
    global _anon_client
    if _anon_client is None:
        settings = get_settings()
        try:
            _anon_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase anon client: {e}")
            raise
    return _anon_client


def get_supabase_service_client() -> Client:
    """
    Returns singleton Supabase client using service role key.
    CRITICAL: This client bypasses PostgreSQL RLS. It must ONLY be used by trusted
    background services (e.g. APScheduler) and MUST explicitly scope all queries with user_id!
    """
    global _service_client
    if _service_client is None:
        settings = get_settings()
        try:
            _service_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase service role client: {e}")
            raise
    return _service_client


def get_user_scoped_client(access_token: str) -> Client:
    """
    Creates or scopes a Supabase client with the authenticated user's access token,
    ensuring all database operations enforce PostgreSQL Row Level Security.
    """
    settings = get_settings()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    # PostgREST client accepts auth header
    client.postgrest.auth(access_token)
    return client
