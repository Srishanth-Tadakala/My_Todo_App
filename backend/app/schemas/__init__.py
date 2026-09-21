"""
Schemas Package Export
"""

from app.schemas.common import PaginatedResponse, ConflictCheckResult, ConflictItem
from app.schemas.auth import SignUpRequest, LoginRequest, RefreshTokenRequest, TokenResponse, UserResponse
from app.schemas.user import ProfileUpdate, ProfileResponse, UserSettingsUpdate, UserSettingsResponse
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.list import TodoListCreate, TodoListUpdate, TodoListResponse, TodoListStats
from app.schemas.todo import (
    TodoStatus, TodoPriority, TodoCreate, TodoUpdate, TodoResponse, TodoReschedule,
    SubtaskCreate, SubtaskUpdate, SubtaskResponse, SubtaskProgress
)
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.timetable import (
    ScheduleType, ExceptionType, TimetableCreate, TimetableUpdate, TimetableResponse,
    ScheduleItemCreate, ScheduleItemUpdate, ScheduleItemResponse,
    ScheduleExceptionCreate, ScheduleExceptionResponse, ScheduleOccurrenceResponse
)
from app.schemas.assignment import AssignmentStatus, AssignmentPriority, AssignmentCreate, AssignmentUpdate, AssignmentResponse
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse
from app.schemas.hackathon import HackathonStatus, HackathonCreate, HackathonUpdate, HackathonResponse
from app.schemas.certification import CertificationStatus, CertificationCreate, CertificationUpdate, CertificationResponse
from app.schemas.internship import InternshipStatus, InternshipCreate, InternshipUpdate, InternshipResponse
from app.schemas.project import ProjectStatus, ProjectCreate, ProjectUpdate, ProjectResponse, ProjectStats
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.schemas.reminder import (
    EntityType, ChannelType, ReminderStatus, ReminderType,
    ReminderCreate, ReminderUpdate, ReminderResponse
)
from app.schemas.notification import DeviceRegisterRequest, DeviceResponse, NotificationLogResponse
from app.schemas.dashboard import DashboardResponse, DashboardTodayStats, DeadlineItem
from app.schemas.calendar import CalendarResponse
from app.schemas.analytics import AnalyticsSummaryResponse
from app.schemas.search import SearchResponse, SearchResultItem
from app.schemas.attachment import AttachmentEntityType, AttachmentCreate, AttachmentResponse, PresignedUploadUrlResponse
