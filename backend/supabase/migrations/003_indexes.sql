-- 003_indexes.sql
-- Performance indexes for Advanced Todo Application

-- Profiles & Settings
CREATE INDEX IF NOT EXISTS idx_profiles_timezone ON public.profiles(timezone);
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON public.user_settings(user_id);

-- Todo Lists
CREATE INDEX IF NOT EXISTS idx_todo_lists_user_id ON public.todo_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_todo_lists_user_deleted ON public.todo_lists(user_id, deleted_at);

-- Projects
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON public.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_user_deleted ON public.projects(user_id, deleted_at);

-- Todos
CREATE INDEX IF NOT EXISTS idx_todos_user_id ON public.todos(user_id);
CREATE INDEX IF NOT EXISTS idx_todos_user_status ON public.todos(user_id, status);
CREATE INDEX IF NOT EXISTS idx_todos_user_due_at ON public.todos(user_id, due_at);
CREATE INDEX IF NOT EXISTS idx_todos_user_deleted ON public.todos(user_id, deleted_at);
CREATE INDEX IF NOT EXISTS idx_todos_list_id ON public.todos(list_id);
CREATE INDEX IF NOT EXISTS idx_todos_project_id ON public.todos(project_id);

-- Subtasks
CREATE INDEX IF NOT EXISTS idx_subtasks_todo_id ON public.subtasks(todo_id);
CREATE INDEX IF NOT EXISTS idx_subtasks_user_id ON public.subtasks(user_id);

-- Tags
CREATE INDEX IF NOT EXISTS idx_tags_user_id ON public.tags(user_id);
CREATE INDEX IF NOT EXISTS idx_todo_tags_todo_id ON public.todo_tags(todo_id);
CREATE INDEX IF NOT EXISTS idx_todo_tags_tag_id ON public.todo_tags(tag_id);

-- Subjects & Timetable
CREATE INDEX IF NOT EXISTS idx_subjects_user_id ON public.subjects(user_id);
CREATE INDEX IF NOT EXISTS idx_timetables_user_id ON public.timetables(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_items_user_id ON public.schedule_items(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_items_timetable ON public.schedule_items(timetable_id);
CREATE INDEX IF NOT EXISTS idx_schedule_items_user_day_time ON public.schedule_items(user_id, day_of_week, start_time);
CREATE INDEX IF NOT EXISTS idx_schedule_items_user_deleted ON public.schedule_items(user_id, deleted_at);
CREATE INDEX IF NOT EXISTS idx_schedule_exceptions_item_date ON public.schedule_exceptions(schedule_item_id, date);

-- Academic
CREATE INDEX IF NOT EXISTS idx_assignments_user_due_at ON public.assignments(user_id, due_at);
CREATE INDEX IF NOT EXISTS idx_assignments_subject_id ON public.assignments(subject_id);
CREATE INDEX IF NOT EXISTS idx_exams_user_exam_date ON public.exams(user_id, exam_date);
CREATE INDEX IF NOT EXISTS idx_exams_subject_id ON public.exams(subject_id);

-- Career
CREATE INDEX IF NOT EXISTS idx_hackathons_user_reg_deadline ON public.hackathons(user_id, registration_deadline);
CREATE INDEX IF NOT EXISTS idx_hackathons_user_sub_deadline ON public.hackathons(user_id, submission_deadline);
CREATE INDEX IF NOT EXISTS idx_certifications_user_exam_date ON public.certifications(user_id, exam_date);
CREATE INDEX IF NOT EXISTS idx_certifications_user_expiry ON public.certifications(user_id, expiry_date);
CREATE INDEX IF NOT EXISTS idx_internships_user_deadline ON public.internships(user_id, application_deadline);
CREATE INDEX IF NOT EXISTS idx_internships_user_status ON public.internships(user_id, status);

-- Events
CREATE INDEX IF NOT EXISTS idx_events_user_start_at ON public.events(user_id, start_at);

-- Reminders (Crucial for background scheduler queries)
CREATE INDEX IF NOT EXISTS idx_reminders_status_remind_at ON public.reminders(status, remind_at);
CREATE INDEX IF NOT EXISTS idx_reminders_user_status_remind_at ON public.reminders(user_id, status, remind_at);
CREATE INDEX IF NOT EXISTS idx_reminders_entity ON public.reminders(entity_type, entity_id);

-- Notification Logs & Devices
CREATE INDEX IF NOT EXISTS idx_notification_logs_user_created ON public.notification_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_devices_user_active ON public.devices(user_id, is_active);

-- Attachments
CREATE INDEX IF NOT EXISTS idx_attachments_user_entity ON public.attachments(user_id, entity_type, entity_id);
