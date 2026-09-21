"""
Hackathon Schemas
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class HackathonStatus(str, Enum):
    INTERESTED = "INTERESTED"
    REGISTERED = "REGISTERED"
    WORKING = "WORKING"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class HackathonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    organizer: Optional[str] = Field(default=None, max_length=100)
    registration_deadline: Optional[str] = None
    submission_deadline: str
    website_url: Optional[str] = Field(default=None, max_length=500)
    team_name: Optional[str] = Field(default=None, max_length=100)
    status: Optional[HackathonStatus] = HackathonStatus.INTERESTED
    notes: Optional[str] = Field(default=None, max_length=1000)


class HackathonUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    organizer: Optional[str] = None
    registration_deadline: Optional[str] = None
    submission_deadline: Optional[str] = None
    website_url: Optional[str] = None
    team_name: Optional[str] = None
    status: Optional[HackathonStatus] = None
    notes: Optional[str] = None


class HackathonResponse(BaseModel):
    id: str
    user_id: str
    name: str
    organizer: Optional[str] = None
    registration_deadline: Optional[str] = None
    submission_deadline: str
    website_url: Optional[str] = None
    team_name: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
