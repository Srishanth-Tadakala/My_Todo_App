"""
Search Router
"""

from fastapi import APIRouter, Depends, Query
from app.core.rate_limit import rate_limit_search
from app.dependencies import get_current_user_id
from app.schemas.search import SearchResponse
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse, dependencies=[Depends(rate_limit_search)])
async def search(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    user_id: str = Depends(get_current_user_id),
):
    """Searches across Todos, Subjects, Assignments, Exams, Hackathons, Certifications, Internships, Projects, and Events."""
    return await search_service.search_all(user_id, q)
