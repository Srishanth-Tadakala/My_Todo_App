"""
Exam Service
Handles Exams and multi-tier customizable reminders (e.g. 7 days, 1 day, 2 hours).
"""

from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple
from app.core.exceptions import NotFoundException
from app.database.repositories import exam_repo
from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.schemas.reminder import EntityType, ReminderType
from app.services.reminder_service import reminder_service
from app.utils.datetime import from_user_timezone, parse_time


class ExamService:
    def __init__(self, e_repo=None, r_service=None):
        self.repo = e_repo or exam_repo
        self.reminder_service = r_service or reminder_service

    async def get_exam(self, exam_id: str, user_id: str) -> ExamResponse:
        item = await self.repo.get_by_id(exam_id, user_id)
        if not item:
            raise NotFoundException("Exam not found.", code="EXAM_NOT_FOUND")
        return ExamResponse(**item)

    async def list_exams(
        self,
        user_id: str,
        subject_id: Optional[str] = None,
        sort_by: str = "exam_date",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ExamResponse], int]:
        items, total = await self.repo.list_exams(
            user_id=user_id,
            subject_id=subject_id,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )
        return [ExamResponse(**i) for i in items], total

    async def create_exam(self, user_id: str, req: ExamCreate) -> ExamResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        res = await self.repo.create(data)
        exam_id = str(res["id"])

        # Schedule multi-tier reminders
        exam_d = date.fromisoformat(req.exam_date)
        exam_t = parse_time(req.start_time)
        exam_dt = datetime.combine(exam_d, exam_t, tzinfo=timezone.utc)

        offsets = req.reminder_offsets or [10080, 1440, 120]  # 7d, 1d, 2h
        for offset_min in offsets:
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.EXAM,
                entity_id=exam_id,
                target_time_utc=exam_dt,
                minutes_before=offset_min,
                reminder_type=ReminderType.DEADLINE_APPROACHING,
            )

        return ExamResponse(**res)

    async def update_exam(self, exam_id: str, user_id: str, req: ExamUpdate) -> ExamResponse:
        data = req.model_dump(exclude_unset=True)
        res = await self.repo.update(exam_id, user_id, data)
        if not res:
            raise NotFoundException("Exam not found.", code="EXAM_NOT_FOUND")

        # If date or time changed, re-schedule reminders
        if "exam_date" in data or "start_time" in data or "reminder_offsets" in data:
            exam_d = date.fromisoformat(res["exam_date"])
            exam_t = parse_time(res["start_time"])
            exam_dt = datetime.combine(exam_d, exam_t, tzinfo=timezone.utc)
            offsets = res.get("reminder_offsets") or [10080, 1440, 120]
            await self.reminder_service.cancel_for_entity(user_id, EntityType.EXAM.value, exam_id)
            for offset_min in offsets:
                await self.reminder_service.schedule_entity_reminder(
                    user_id=user_id,
                    entity_type=EntityType.EXAM,
                    entity_id=exam_id,
                    target_time_utc=exam_dt,
                    minutes_before=offset_min,
                    reminder_type=ReminderType.DEADLINE_APPROACHING,
                )

        return ExamResponse(**res)

    async def delete_exam(self, exam_id: str, user_id: str) -> bool:
        deleted = await self.repo.delete(exam_id, user_id)
        if not deleted:
            raise NotFoundException("Exam not found.", code="EXAM_NOT_FOUND")
        await self.reminder_service.cancel_for_entity(user_id, EntityType.EXAM.value, exam_id)
        return True


exam_service = ExamService()
