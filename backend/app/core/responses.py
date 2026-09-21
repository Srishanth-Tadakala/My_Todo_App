"""
Standard API Response Envelopes
Ensures all API responses follow a uniform structure.
"""

from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel
from fastapi.responses import JSONResponse

T = TypeVar("T")


class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[APIError] = None
    meta: Optional[Dict[str, Any]] = None


def success_response(
    data: Any = None,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> JSONResponse:
    """Builds a standardized success JSONResponse."""
    payload = {
        "success": True,
        "data": data,
        "error": None,
    }
    if meta is not None:
        payload["meta"] = meta
    return JSONResponse(status_code=status_code, content=payload)


def error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Any] = None,
) -> JSONResponse:
    """Builds a standardized error JSONResponse."""
    payload = {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }
    return JSONResponse(status_code=status_code, content=payload)
