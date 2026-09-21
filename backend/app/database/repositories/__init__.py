"""
Repository Registry and Exports
"""

from app.database.repositories.user_repo import UserRepository
from app.database.repositories.todo_repo import TodoListRepository, TodoRepository
from app.database.repositories.timetable_repo import SubjectRepository, TimetableRepository
from app.database.repositories.academic_repo import AssignmentRepository, ExamRepository
from app.database.repositories.career_repo import HackathonRepository, CertificationRepository, InternshipRepository
from app.database.repositories.project_repo import ProjectRepository
from app.database.repositories.event_repo import EventRepository
from app.database.repositories.reminder_repo import ReminderRepository
from app.database.repositories.notification_repo import DeviceRepository, NotificationLogRepository, AttachmentRepository

# Global singleton repository instances
user_repo = UserRepository()
todo_list_repo = TodoListRepository()
todo_repo = TodoRepository()
subject_repo = SubjectRepository()
timetable_repo = TimetableRepository()
assignment_repo = AssignmentRepository()
exam_repo = ExamRepository()
hackathon_repo = HackathonRepository()
cert_repo = CertificationRepository()
internship_repo = InternshipRepository()
project_repo = ProjectRepository()
event_repo = EventRepository()
reminder_repo = ReminderRepository()
device_repo = DeviceRepository()
notification_log_repo = NotificationLogRepository()
attachment_repo = AttachmentRepository()
