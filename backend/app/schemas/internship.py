"""
Internship Application Schemas
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InternshipStatus(str, Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class InternshipCreate(BaseModel):
    company: str = Field(min_length=1, max_length=150)
    role: str = Field(min_length=1, max_length=150)
    application_deadline: Optional[str] = None
    application_url: Optional[str] = Field(default=None, max_length=500)
    status: Optional[InternshipStatus] = InternshipStatus.SAVED
    applied_at: Optional[str] = None
    interview_at: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=1000)


class InternshipUpdate(BaseModel):
    company: Optional[str] = Field(default=None, min_length=1, max_length=150)
    role: Optional[str] = Field(default=None, min_length=1, max_length=150)
    application_deadline: Optional[str] = None
    application_url: Optional[str] = None
    status: Optional[InternshipStatus] = None
    applied_at: Optional[str] = None
    interview_at: Optional[str] = None
    notes: Optional[str] = None


class InternshipResponse(BaseModel):
    id: str
    user_id: str
    company: str
    role: str
    application_deadline: Optional[str] = None
    application_url: Optional[str] = None
    status: str
    applied_at: Optional[str] = None
    interview_at: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
