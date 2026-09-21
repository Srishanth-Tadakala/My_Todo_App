"""
Custom Application Exceptions
"""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundException(AppException):
    """Raised when an entity is not found."""

    def __init__(self, message: str = "Resource not found.", code: str = "NOT_FOUND", details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=404, details=details)


class UnauthorizedException(AppException):
    """Raised when authentication is missing or invalid."""

    def __init__(self, message: str = "Authentication required.", code: str = "UNAUTHORIZED", details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=401, details=details)


class ForbiddenException(AppException):
    """Raised when a user lacks permission to perform an action."""

    def __init__(self, message: str = "Access forbidden.", code: str = "FORBIDDEN", details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=403, details=details)


class ConflictException(AppException):
    """Raised when a conflict occurs (e.g. duplicate key or schedule overlap)."""

    def __init__(self, message: str = "Resource conflict.", code: str = "CONFLICT", details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=409, details=details)


class ValidationException(AppException):
    """Raised when request payload or business validation fails."""

    def __init__(self, message: str = "Validation failed.", code: str = "VALIDATION_ERROR", details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=422, details=details)


class DatabaseException(AppException):
    """Raised when an unexpected database error occurs."""

    def __init__(self, message: str = "Database operation failed.", code: str = "DATABASE_ERROR", details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=500, details=details)


class RateLimitException(AppException):
    """Raised when client exceeds rate limit."""

    def __init__(self, message: str = "Too many requests. Please try again later.", code: str = "RATE_LIMIT_EXCEEDED", details: Optional[Any] = None):
        super().__init__(message=message, code=code, status_code=429, details=details)
