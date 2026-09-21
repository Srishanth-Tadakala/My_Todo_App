-- seed.sql
-- Development Seed Data for Advanced Todo Application
-- Replace '00000000-0000-0000-0000-000000000001' with your actual Supabase auth user UUID if inserting manually.

DO $$
DECLARE
    v_user_id UUID := '00000000-0000-0000-0000-000000000001';
    v_list_college UUID := gen_random_uuid();
    v_list_personal UUID := gen_random_uuid();
    v_subject_dbms UUID := gen_random_uuid();
    v_subject_os UUID := gen_random_uuid();
    v_subject_cn UUID := gen_random_uuid();
    v_timetable_id UUID := gen_random_uuid();
    v_project_id UUID := gen_random_uuid();
    v_todo_1 UUID := gen_random_uuid();
BEGIN
    -- 1. Profile & Settings (Only if auth.users entry exists or in dev)
    INSERT INTO public.profiles (id, full_name, avatar_url, timezone)
    VALUES (v_user_id, 'Alex Student', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb', 'Asia/Kolkata')
    ON CONFLICT (id) DO UPDATE SET full_name = EXCLUDED.full_name;

    INSERT INTO public.user_settings (user_id, default_reminder_minutes, quiet_hours_enabled, quiet_hours_start, quiet_hours_end, timezone)
    VALUES (v_user_id, 30, TRUE, '22:00:00', '07:00:00', 'Asia/Kolkata')
    ON CONFLICT (user_id) DO NOTHING;

    -- 2. Todo Lists
    INSERT INTO public.todo_lists (id, user_id, name, description, icon, color, sort_order)
    VALUES 
        (v_list_college, v_user_id, 'College & Academics', 'Coursework, exams, and lecture tasks', 'school', '#3B82F6', 1),
        (v_list_personal, v_user_id, 'Personal Growth', 'Fitness, habits, and side projects', 'user', '#10B981', 2);

    -- 3. Projects
    INSERT INTO public.projects (id, user_id, name, description, status, start_date, target_date)
    VALUES (v_project_id, v_user_id, 'Compiler Design Lab', 'Mini compiler implementation in C++', 'ACTIVE', CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days');

    -- 4. Todos
    INSERT INTO public.todos (id, user_id, list_id, project_id, title, description, status, priority, due_at, estimated_minutes)
    VALUES 
        (v_todo_1, v_user_id, v_list_college, v_project_id, 'Complete Lexical Analyzer', 'Implement tokenization for keywords and identifiers', 'IN_PROGRESS', 'HIGH', NOW() + INTERVAL '2 days', 180),
        (gen_random_uuid(), v_user_id, v_list_college, NULL, 'Read Operating Systems Chapter 4', 'Process synchronization and mutex semaphores', 'TODO', 'MEDIUM', NOW() + INTERVAL '3 days', 60),
        (gen_random_uuid(), v_user_id, v_list_college, NULL, 'Submit Computer Networks Lab 3', 'Packet tracing with Wireshark', 'TODO', 'URGENT', NOW() + INTERVAL '1 day', 90),
        (gen_random_uuid(), v_user_id, v_list_personal, NULL, 'Gym: Upper Body Workout', 'Bench press, pull-ups, overhead press', 'COMPLETED', 'LOW', NOW() - INTERVAL '4 hours', 45),
        (gen_random_uuid(), v_user_id, v_list_personal, NULL, 'Review React Native Navigation docs', 'Explore Expo Router and tab navigators', 'TODO', 'MEDIUM', NOW() + INTERVAL '4 days', 75);

    -- 5. Subtasks for Todo 1
    INSERT INTO public.subtasks (todo_id, user_id, title, is_completed, sort_order)
    VALUES 
        (v_todo_1, v_user_id, 'Define regular expressions for keywords', TRUE, 1),
        (v_todo_1, v_user_id, 'Build transition state diagram', TRUE, 2),
        (v_todo_1, v_user_id, 'Write C++ driver code', FALSE, 3);

    -- 6. Subjects
    INSERT INTO public.subjects (id, user_id, name, code, teacher, semester, academic_year, color)
    VALUES 
        (v_subject_dbms, v_user_id, 'Database Management Systems', 'CS301', 'Dr. Ramesh Kumar', 'Semester 5', '2026-2027', '#6366F1'),
        (v_subject_os, v_user_id, 'Operating Systems', 'CS302', 'Prof. Anita Sharma', 'Semester 5', '2026-2027', '#EC4899'),
        (v_subject_cn, v_user_id, 'Computer Networks', 'CS303', 'Dr. Michael Chen', 'Semester 5', '2026-2027', '#14B8A6');

    -- 7. Timetable & Schedule Items (5 Classes)
    INSERT INTO public.timetables (id, user_id, name, academic_year, semester, is_active)
    VALUES (v_timetable_id, v_user_id, 'Fall 2026 Timetable', '2026-2027', 'Semester 5', TRUE);

    INSERT INTO public.schedule_items (user_id, timetable_id, subject_id, title, type, day_of_week, start_time, end_time, building, floor, room, teacher)
    VALUES 
        (v_user_id, v_timetable_id, v_subject_dbms, 'DBMS Lecture', 'CLASS', 0, '09:00:00', '10:00:00', 'Tech Block', '2nd Floor', 'LH-201', 'Dr. Ramesh Kumar'),
        (v_user_id, v_timetable_id, v_subject_os, 'OS Lecture', 'CLASS', 0, '10:15:00', '11:15:00', 'Tech Block', '2nd Floor', 'LH-203', 'Prof. Anita Sharma'),
        (v_user_id, v_timetable_id, v_subject_cn, 'Computer Networks', 'CLASS', 1, '11:30:00', '12:30:00', 'Science Wing', '1st Floor', 'SW-105', 'Dr. Michael Chen'),
        (v_user_id, v_timetable_id, v_subject_dbms, 'DBMS Lab', 'CLASS', 2, '14:00:00', '16:00:00', 'IT Center', 'Ground Floor', 'Lab-4', 'Dr. Ramesh Kumar'),
        (v_user_id, v_timetable_id, NULL, 'Competitive Coding Session', 'STUDY', 3, '16:30:00', '18:00:00', 'Library', '3rd Floor', 'Study Hall B', 'Self');

    -- 8. Assignments (3)
    INSERT INTO public.assignments (user_id, subject_id, title, description, assigned_at, due_at, priority, status)
    VALUES 
        (v_user_id, v_subject_dbms, 'SQL Query Optimization Problem Set', 'Solve 10 complex queries using B-Tree indexing and query plans', NOW() - INTERVAL '3 days', NOW() + INTERVAL '2 days', 'HIGH', 'IN_PROGRESS'),
        (v_user_id, v_subject_os, 'Deadlock Banker''s Algorithm Simulation', 'Write multi-threaded simulation of Banker''s safety check', NOW() - INTERVAL '5 days', NOW() + INTERVAL '4 days', 'MEDIUM', 'NOT_STARTED'),
        (v_user_id, v_subject_cn, 'Subnetting & CIDR Calculation', 'Compute host ranges for 5 enterprise networks', NOW() - INTERVAL '7 days', NOW() - INTERVAL '1 day', 'LOW', 'COMPLETED');

    -- 9. Exams (2)
    INSERT INTO public.exams (user_id, subject_id, title, exam_date, start_time, end_time, building, floor, room, syllabus)
    VALUES 
        (v_user_id, v_subject_dbms, 'DBMS Mid-Semester Examination', CURRENT_DATE + INTERVAL '12 days', '10:00:00', '12:00:00', 'Exam Hall', 'Ground Floor', 'Hall A', 'ER Model, Relational Algebra, SQL, Normalization 1NF-BCNF'),
        (v_user_id, v_subject_os, 'Operating Systems Quiz 2', CURRENT_DATE + INTERVAL '18 days', '14:00:00', '15:00:00', 'Tech Block', '2nd Floor', 'LH-203', 'Process Scheduling & Memory Virtualization');

    -- 10. Hackathons (2)
    INSERT INTO public.hackathons (user_id, name, organizer, registration_deadline, submission_deadline, website_url, team_name, status)
    VALUES 
        (v_user_id, 'HackGlobal 2026', 'Major League Hacking', NOW() + INTERVAL '10 days', NOW() + INTERVAL '25 days', 'https://hackglobal2026.devpost.com', 'ByteForce', 'REGISTERED'),
        (v_user_id, 'Smart India Tech Fest', 'Govt Innovation Cell', NOW() + INTERVAL '40 days', NOW() + INTERVAL '55 days', 'https://smartindiafest.org', 'InnovateX', 'INTERESTED');

    -- 11. Certifications (2)
    INSERT INTO public.certifications (user_id, name, provider, registration_deadline, exam_date, status)
    VALUES 
        (v_user_id, 'AWS Certified Solutions Architect - Associate', 'Amazon Web Services', NOW() + INTERVAL '30 days', NOW() + INTERVAL '45 days', 'IN_PROGRESS'),
        (v_user_id, 'PostgreSQL Database Associate', 'PostgreSQL Professional', NOW() + INTERVAL '60 days', NOW() + INTERVAL '90 days', 'PLANNED');

    -- 12. Internship Applications (2)
    INSERT INTO public.internships (user_id, company, role, application_deadline, application_url, status, applied_at)
    VALUES 
        (v_user_id, 'Stripe', 'Software Engineering Intern (Backend)', NOW() + INTERVAL '15 days', 'https://stripe.com/jobs/intern', 'APPLIED', NOW() - INTERVAL '4 days'),
        (v_user_id, 'Datadog', 'Distributed Systems Intern', NOW() + INTERVAL '20 days', 'https://datadoghq.com/careers', 'INTERVIEW', NOW() - INTERVAL '10 days');

    -- 13. Personal Events (2)
    INSERT INTO public.events (user_id, title, description, start_at, end_at, location, reminder_enabled, reminder_minutes)
    VALUES 
        (v_user_id, 'Campus Tech Club Meetup', 'Discussion on building mobile apps with Expo and FastAPI', NOW() + INTERVAL '5 days' + INTERVAL '3 hours', NOW() + INTERVAL '5 days' + INTERVAL '5 hours', 'Auditorium 2', TRUE, 60),
        (v_user_id, 'Quarterly Doctor Appointment', 'Routine health checkup', NOW() + INTERVAL '8 days' + INTERVAL '2 hours', NOW() + INTERVAL '8 days' + INTERVAL '3 hours', 'City Health Clinic', TRUE, 120);

END $$;
