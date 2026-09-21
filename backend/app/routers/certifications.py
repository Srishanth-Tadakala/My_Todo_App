"""
Certifications Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.certification import CertificationCreate, CertificationResponse, CertificationStatus, CertificationUpdate
from app.schemas.common import PaginatedResponse
from app.services.certification_service import certification_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/certifications", tags=["Certifications"])


@router.get("", response_model=PaginatedResponse[CertificationResponse])
async def list_certifications(
    status: Optional[CertificationStatus] = Query(None),
    sort_by: str = Query("exam_date"),
    ascending: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists certifications with status filtering and pagination."""
    items, total = await certification_service.list_certifications(
        user_id=user_id,
        status=status.value if status else None,
        sort_by=sort_by,
        ascending=ascending,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=CertificationResponse, status_code=201)
async def create_certification(req: CertificationCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new certification and sets exam/expiration reminders."""
    return await certification_service.create_certification(user_id, req)


@router.get("/{cert_id}", response_model=CertificationResponse)
async def get_certification(cert_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves certification by ID."""
    return await certification_service.get_certification(cert_id, user_id)


@router.put("/{cert_id}", response_model=CertificationResponse)
async def update_certification(
    cert_id: str,
    req: CertificationUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates certification status or credential details."""
    return await certification_service.update_certification(cert_id, user_id, req)


@router.delete("/{cert_id}", status_code=200)
async def delete_certification(cert_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes a certification and cancels its reminders."""
    await certification_service.delete_certification(cert_id, user_id)
    return success_response({"message": "Certification deleted successfully."})
