-- 001_initial_schema.sql
-- Complete PostgreSQL schema for the Advanced Todo Application

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Profiles (matches Supabase Auth user id)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    avatar_url TEXT,
    timezone TEXT NOT NULL DEFAULT 'UTC',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. User Settings
CREATE TABLE IF NOT EXISTS public.user_settings (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    default_reminder_minutes INTEGER NOT NULL DEFAULT 30,
    quiet_hours_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    quiet_hours_start TIME NOT NULL DEFAULT '22:00:00',
    quiet_hours_end TIME NOT NULL DEFAULT '07:00:00',
    timezone TEXT NOT NULL DEFAULT 'UTC',
    daily_summary_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    daily_summary_time TIME NOT NULL DEFAULT '08:00:00',
    weekly_summary_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sound_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    vibration_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Todo Lists
CREATE TABLE IF NOT EXISTS public.todo_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    color TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Projects
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'PLANNING',
    start_date DATE,
    target_date DATE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Todos
CREATE TABLE IF NOT EXISTS public.todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    list_id UUID REFERENCES public.todo_lists(id) ON DELETE SET NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'TODO', -- TODO, IN_PROGRESS, COMPLETED, CANCELLED
    priority TEXT NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, URGENT
    due_at TIMESTAMPTZ,
    timezone TEXT NOT NULL DEFAULT 'UTC',
    estimated_minutes INTEGER,
    actual_minutes INTEGER,
    reminder_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    postponed_count INTEGER NOT NULL DEFAULT 0,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Subtasks
CREATE TABLE IF NOT EXISTS public.subtasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    todo_id UUID NOT NULL REFERENCES public.todos(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Tags
CREATE TABLE IF NOT EXISTS public.tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_tag_name_user UNIQUE (user_id, name)
);

-- 8. Todo Tags (Many-to-Many)
CREATE TABLE IF NOT EXISTS public.todo_tags (
    todo_id UUID NOT NULL REFERENCES public.todos(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES public.tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (todo_id, tag_id)
);

-- 9. Subjects
CREATE TABLE IF NOT EXISTS public.subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    code TEXT,
    teacher TEXT,
    semester TEXT,
    academic_year TEXT,
    color TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10. Timetables
CREATE TABLE IF NOT EXISTS public.timetables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    academic_year TEXT,
    semester TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11. Schedule Items
CREATE TABLE IF NOT EXISTS public.schedule_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    timetable_id UUID NOT NULL REFERENCES public.timetables(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'CLASS', -- CLASS, STUDY, PROJECT, WORK, MEETING, FITNESS, PERSONAL, BREAK, OTHER
    day_of_week INTEGER NOT NULL, -- 0=Monday, 6=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    repeat_rule JSONB, -- Optional extra recurrence specification
    building TEXT,
    floor TEXT,
    room TEXT,
    teacher TEXT,
    reminder_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    reminder_minutes INTEGER NOT NULL DEFAULT 15,
    notes TEXT,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 12. Schedule Exceptions
CREATE TABLE IF NOT EXISTS public.schedule_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_item_id UUID NOT NULL REFERENCES public.schedule_items(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    exception_type TEXT NOT NULL, -- CANCELLED, RESCHEDULED, LOCATION_CHANGED, TIME_CHANGED
    new_start_time TIME,
    new_end_time TIME,
    new_building TEXT,
    new_floor TEXT,
    new_room TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_exception_item_date UNIQUE (schedule_item_id, date)
);

-- 13. Assignments
CREATE TABLE IF NOT EXISTS public.assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    assigned_at TIMESTAMPTZ,
    due_at TIMESTAMPTZ NOT NULL,
    priority TEXT NOT NULL DEFAULT 'MEDIUM',
    status TEXT NOT NULL DEFAULT 'NOT_STARTED', -- NOT_STARTED, IN_PROGRESS, SUBMITTED, COMPLETED
    submission_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 14. Exams
CREATE TABLE IF NOT EXISTS public.exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES public.subjects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    exam_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    building TEXT,
    floor TEXT,
    room TEXT,
    syllabus TEXT,
    notes TEXT,
    reminder_offsets JSONB DEFAULT '[10080, 1440, 120]'::jsonb, -- default: 7 days, 1 day, 2 hours
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 15. Hackathons
CREATE TABLE IF NOT EXISTS public.hackathons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    organizer TEXT,
    registration_deadline TIMESTAMPTZ,
    submission_deadline TIMESTAMPTZ NOT NULL,
    website_url TEXT,
    team_name TEXT,
    status TEXT NOT NULL DEFAULT 'INTERESTED', -- INTERESTED, REGISTERED, WORKING, SUBMITTED, COMPLETED, CANCELLED
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 16. Certifications
CREATE TABLE IF NOT EXISTS public.certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    provider TEXT,
    registration_deadline TIMESTAMPTZ,
    exam_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    website_url TEXT,
    credential_id TEXT,
    status TEXT NOT NULL DEFAULT 'PLANNED', -- PLANNED, IN_PROGRESS, EARNED, EXPIRED
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 17. Internships
CREATE TABLE IF NOT EXISTS public.internships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    application_deadline TIMESTAMPTZ,
    application_url TEXT,
    status TEXT NOT NULL DEFAULT 'SAVED', -- SAVED, APPLIED, ASSESSMENT, INTERVIEW, OFFER, ACCEPTED, REJECTED, WITHDRAWN
    applied_at TIMESTAMPTZ,
    interview_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 18. Personal Events
CREATE TABLE IF NOT EXISTS public.events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NOT NULL,
    location TEXT,
    reminder_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    reminder_minutes INTEGER NOT NULL DEFAULT 30,
    repeat_rule JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 19. Reminders
CREATE TABLE IF NOT EXISTS public.reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL, -- TODO, SCHEDULE, ASSIGNMENT, EXAM, HACKATHON, CERTIFICATION, INTERNSHIP, EVENT
    entity_id UUID NOT NULL,
    reminder_type TEXT NOT NULL DEFAULT 'DUE_SOON', -- DUE_SOON, DUE_NOW, OVERDUE, CLASS_STARTING, DEADLINE_APPROACHING, etc.
    remind_at TIMESTAMPTZ NOT NULL,
    channel TEXT NOT NULL DEFAULT 'PUSH', -- PUSH, IN_APP
    status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, SENT, FAILED, CANCELLED
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    next_retry_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 20. Notification Logs
CREATE TABLE IF NOT EXISTS public.notification_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    reminder_id UUID REFERENCES public.reminders(id) ON DELETE SET NULL,
    notification_type TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    channel TEXT NOT NULL DEFAULT 'PUSH',
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'SENT', -- SENT, FAILED
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_notification_dedup UNIQUE (user_id, entity_type, entity_id, reminder_id, notification_type)
);

-- 21. Devices (Expo Push Notification tokens)
CREATE TABLE IF NOT EXISTS public.devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    expo_push_token TEXT NOT NULL,
    platform TEXT NOT NULL, -- ios, android, web
    device_name TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_device_token UNIQUE (user_id, expo_push_token)
);

-- 22. Attachments
CREATE TABLE IF NOT EXISTS public.attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL, -- TODO, ASSIGNMENT, CERTIFICATION, PROJECT
    entity_id UUID NOT NULL,
    file_name TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
