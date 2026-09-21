"""
Attachment and Storage Service
Integrates with Supabase Storage for secure file uploads and presigned download URLs.
"""

from typing import List, Optional
import uuid
from app.config import get_settings
from app.core.exceptions import NotFoundException
from app.database.repositories import attachment_repo
from app.database.supabase import get_supabase_service_client
from app.schemas.attachment import AttachmentCreate, AttachmentResponse, PresignedUploadUrlResponse

STORAGE_BUCKET = "todo-attachments"


class AttachmentService:
    def __init__(self, a_repo=None):
        self.repo = a_repo or attachment_repo

    async def generate_upload_url(
        self,
        user_id: str,
        entity_type: str,
        file_name: str,
    ) -> PresignedUploadUrlResponse:
        """Generates a presigned storage upload path for the client."""
        file_ext = file_name.split(".")[-1] if "." in file_name else "dat"
        storage_path = f"{user_id}/{entity_type.lower()}/{uuid.uuid4()}.{file_ext}"

        # In testing or mock mode, generate standard direct mock URL
        settings = get_settings()
        if settings.is_testing or "dummy" in settings.SUPABASE_ANON_KEY:
            upload_url = f"https://mock-storage.supabase.co/upload/{STORAGE_BUCKET}/{storage_path}"
        else:
            try:
                client = get_supabase_service_client()
                # Create signed upload URL
                res = client.storage.from_(STORAGE_BUCKET).create_signed_upload_url(storage_path)
                upload_url = res.get("signed_url") or res.get("url") or ""
            except Exception:
                upload_url = f"{settings.SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{storage_path}"

        return PresignedUploadUrlResponse(
            storage_path=storage_path,
            upload_url=upload_url,
            expires_in=3600,
        )

    async def record_attachment(self, user_id: str, req: AttachmentCreate) -> AttachmentResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        data["entity_type"] = req.entity_type.value
        res = await self.repo.create(data)

        # Generate download url
        download_url = await self._get_download_url(res["storage_path"])
        return AttachmentResponse(**res, download_url=download_url)

    async def list_attachments(self, user_id: str, entity_type: str, entity_id: str) -> List[AttachmentResponse]:
        items = await self.repo.list_for_entity(user_id, entity_type, entity_id)
        results = []
        for it in items:
            dl_url = await self._get_download_url(it["storage_path"])
            results.append(AttachmentResponse(**it, download_url=dl_url))
        return results

    async def delete_attachment(self, attachment_id: str, user_id: str) -> bool:
        item = await self.repo.get_by_id(attachment_id, user_id)
        if not item:
            raise NotFoundException("Attachment not found.", code="ATTACHMENT_NOT_FOUND")

        # Try to delete from Supabase storage
        settings = get_settings()
        if not settings.is_testing and "dummy" not in settings.SUPABASE_ANON_KEY:
            try:
                client = get_supabase_service_client()
                client.storage.from_(STORAGE_BUCKET).remove([item["storage_path"]])
            except Exception:
                pass

        return await self.repo.delete(attachment_id, user_id)

    async def _get_download_url(self, storage_path: str) -> str:
        settings = get_settings()
        if settings.is_testing or "dummy" in settings.SUPABASE_ANON_KEY:
            return f"https://mock-storage.supabase.co/download/{STORAGE_BUCKET}/{storage_path}"
        try:
            client = get_supabase_service_client()
            res = client.storage.from_(STORAGE_BUCKET).create_signed_url(storage_path, 3600)
            return res.get("signedURL") or ""
        except Exception:
            return f"{settings.SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{storage_path}"


attachment_service = AttachmentService()
