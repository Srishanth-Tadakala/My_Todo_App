"""
Certification Service
"""

from typing import List, Optional, Tuple
from app.core.exceptions import NotFoundException
from app.database.repositories import cert_repo
from app.schemas.certification import CertificationCreate, CertificationResponse, CertificationUpdate
from app.schemas.reminder import EntityType, ReminderType
from app.services.reminder_service import reminder_service
from app.utils.datetime import parse_datetime


class CertificationService:
    def __init__(self, c_repo=None, r_service=None):
        self.repo = c_repo or cert_repo
        self.reminder_service = r_service or reminder_service

    async def get_certification(self, cert_id: str, user_id: str) -> CertificationResponse:
        item = await self.repo.get_by_id(cert_id, user_id)
        if not item:
            raise NotFoundException("Certification not found.", code="CERTIFICATION_NOT_FOUND")
        return CertificationResponse(**item)

    async def list_certifications(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort_by: str = "exam_date",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[CertificationResponse], int]:
        items, total = await self.repo.list_certifications(
            user_id=user_id,
            status=status,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )
        return [CertificationResponse(**i) for i in items], total

    async def create_certification(self, user_id: str, req: CertificationCreate) -> CertificationResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        data["status"] = req.status.value if req.status else "PLANNED"
        res = await self.repo.create(data)
        cert_id = str(res["id"])

        # Reminders for exam (7d) and expiry (30d)
        if req.exam_date:
            ex_dt = parse_datetime(req.exam_date)
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.CERTIFICATION,
                entity_id=cert_id,
                target_time_utc=ex_dt,
                minutes_before=10080,  # 7 days
                reminder_type=ReminderType.DEADLINE_APPROACHING,
            )

        if req.expiry_date:
            exp_dt = parse_datetime(req.expiry_date)
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.CERTIFICATION,
                entity_id=cert_id,
                target_time_utc=exp_dt,
                minutes_before=43200,  # 30 days
                reminder_type=ReminderType.CERTIFICATION_EXPIRING,
            )

        return CertificationResponse(**res)

    async def update_certification(self, cert_id: str, user_id: str, req: CertificationUpdate) -> CertificationResponse:
        data = req.model_dump(exclude_unset=True)
        if "status" in data and data["status"]:
            data["status"] = req.status.value
            if data["status"] in ("EARNED", "EXPIRED"):
                await self.reminder_service.cancel_for_entity(user_id, EntityType.CERTIFICATION.value, cert_id)

        res = await self.repo.update(cert_id, user_id, data)
        if not res:
            raise NotFoundException("Certification not found.", code="CERTIFICATION_NOT_FOUND")
        return CertificationResponse(**res)

    async def delete_certification(self, cert_id: str, user_id: str) -> bool:
        deleted = await self.repo.delete(cert_id, user_id)
        if not deleted:
            raise NotFoundException("Certification not found.", code="CERTIFICATION_NOT_FOUND")
        await self.reminder_service.cancel_for_entity(user_id, EntityType.CERTIFICATION.value, cert_id)
        return True


certification_service = CertificationService()
