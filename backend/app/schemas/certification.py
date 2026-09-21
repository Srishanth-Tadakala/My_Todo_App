"""
Certification Schemas
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CertificationStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    EARNED = "EARNED"
    EXPIRED = "EXPIRED"


class CertificationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    provider: Optional[str] = Field(default=None, max_length=100)
    registration_deadline: Optional[str] = None
    exam_date: Optional[str] = None
    expiry_date: Optional[str] = None
    website_url: Optional[str] = Field(default=None, max_length=500)
    credential_id: Optional[str] = Field(default=None, max_length=100)
    status: Optional[CertificationStatus] = CertificationStatus.PLANNED
    notes: Optional[str] = Field(default=None, max_length=1000)


class CertificationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    provider: Optional[str] = None
    registration_deadline: Optional[str] = None
    exam_date: Optional[str] = None
    expiry_date: Optional[str] = None
    website_url: Optional[str] = None
    credential_id: Optional[str] = None
    status: Optional[CertificationStatus] = None
    notes: Optional[str] = None


class CertificationResponse(BaseModel):
    id: str
    user_id: str
    name: str
    provider: Optional[str] = None
    registration_deadline: Optional[str] = None
    exam_date: Optional[str] = None
    expiry_date: Optional[str] = None
    website_url: Optional[str] = None
    credential_id: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
