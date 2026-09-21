"""
Application Configuration
Loads settings from environment variables using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase Credentials
    SUPABASE_URL: str = Field(default="https://example.supabase.co")
    SUPABASE_ANON_KEY: str = Field(default="dummy-anon-key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="dummy-service-role-key")

    # Expo Push Notifications
    EXPO_ACCESS_TOKEN: Optional[str] = Field(default=None)

    # Application Settings
    APP_ENV: str = Field(default="development")
    API_PREFIX: str = Field(default="/api/v1")
    LOG_LEVEL: str = Field(default="INFO")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    ALLOWED_ORIGINS: str = Field(default="*")

    # Scheduler Settings
    REMINDER_CHECK_INTERVAL_SECONDS: int = Field(default=30)
    OVERDUE_CHECK_INTERVAL_SECONDS: int = Field(default=300)

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV.lower() == "testing"

    @property
    def cors_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Returns cached instance of the application settings."""
    return Settings()
