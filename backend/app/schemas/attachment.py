"""
Attachment and Storage Schemas
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AttachmentEntityType(str, Enum):
    TODO = "TODO"
    ASSIGNMENT = "ASSIGNMENT"
    CERTIFICATION = "CERTIFICATION"
    PROJECT = "PROJECT"


class AttachmentCreate(BaseModel):
    entity_type: AttachmentEntityType
    entity_id: str
    file_name: str = Field(min_length=1, max_length=255)
    storage_path: str = Field(min_length=1, max_length=500)
    mime_type: str = Field(min_length=1, max_length=100)
    file_size: int = Field(ge=0)


class AttachmentResponse(BaseModel):
    id: str
    user_id: str
    entity_type: str
    entity_id: str
    file_name: str
    storage_path: str
    mime_type: str
    file_size: int
    download_url: Optional[str] = None
    created_at: Optional[str] = None


class PresignedUploadUrlResponse(BaseModel):
    storage_path: str
    upload_url: str
    expires_in: int = 3600
