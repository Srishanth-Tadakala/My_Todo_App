"""
Attachments Router
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.attachment import (
    AttachmentCreate, AttachmentEntityType, AttachmentResponse, PresignedUploadUrlResponse
)
from app.services.attachment_service import attachment_service

router = APIRouter(prefix="/attachments", tags=["Attachments"])


@router.post("/upload-url", response_model=PresignedUploadUrlResponse)
async def get_upload_url(
    entity_type: AttachmentEntityType = Query(...),
    file_name: str = Query(...),
    user_id: str = Depends(get_current_user_id),
):
    """Generates a presigned upload URL for Supabase Storage."""
    return await attachment_service.generate_upload_url(user_id, entity_type.value, file_name)


@router.post("/record", response_model=AttachmentResponse, status_code=201)
async def record_attachment(
    req: AttachmentCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Saves attachment metadata after client uploads file to Supabase Storage."""
    return await attachment_service.record_attachment(user_id, req)


@router.get("/{entity_type}/{entity_id}", response_model=List[AttachmentResponse])
async def list_attachments(
    entity_type: AttachmentEntityType,
    entity_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Lists attachments for a specific entity with presigned download URLs."""
    return await attachment_service.list_attachments(user_id, entity_type.value, entity_id)


@router.delete("/{attachment_id}", status_code=200)
async def delete_attachment(
    attachment_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Deletes attachment record and cleans up storage object."""
    await attachment_service.delete_attachment(attachment_id, user_id)
    return success_response({"message": "Attachment deleted successfully."})
