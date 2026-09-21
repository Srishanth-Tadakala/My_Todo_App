-- 002_rls_policies.sql
-- Enable Row Level Security (RLS) on all user-owned tables

-- 1. Profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- 2. User Settings
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own settings" ON public.user_settings FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own settings" ON public.user_settings FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own settings" ON public.user_settings FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 3. Todo Lists
ALTER TABLE public.todo_lists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own lists" ON public.todo_lists FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own lists" ON public.todo_lists FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own lists" ON public.todo_lists FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own lists" ON public.todo_lists FOR DELETE USING (auth.uid() = user_id);

-- 4. Projects
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own projects" ON public.projects FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own projects" ON public.projects FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own projects" ON public.projects FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own projects" ON public.projects FOR DELETE USING (auth.uid() = user_id);

-- 5. Todos
ALTER TABLE public.todos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own todos" ON public.todos FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own todos" ON public.todos FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own todos" ON public.todos FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own todos" ON public.todos FOR DELETE USING (auth.uid() = user_id);

-- 6. Subtasks
ALTER TABLE public.subtasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own subtasks" ON public.subtasks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own subtasks" ON public.subtasks FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own subtasks" ON public.subtasks FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own subtasks" ON public.subtasks FOR DELETE USING (auth.uid() = user_id);

-- 7. Tags
ALTER TABLE public.tags ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own tags" ON public.tags FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own tags" ON public.tags FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own tags" ON public.tags FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own tags" ON public.tags FOR DELETE USING (auth.uid() = user_id);

-- 8. Todo Tags
ALTER TABLE public.todo_tags ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own todo tags" ON public.todo_tags FOR SELECT
    USING (EXISTS (SELECT 1 FROM public.todos WHERE todos.id = todo_tags.todo_id AND todos.user_id = auth.uid()));
CREATE POLICY "Users can insert own todo tags" ON public.todo_tags FOR INSERT
    WITH CHECK (EXISTS (SELECT 1 FROM public.todos WHERE todos.id = todo_tags.todo_id AND todos.user_id = auth.uid()));
CREATE POLICY "Users can delete own todo tags" ON public.todo_tags FOR DELETE
    USING (EXISTS (SELECT 1 FROM public.todos WHERE todos.id = todo_tags.todo_id AND todos.user_id = auth.uid()));

-- 9. Subjects
ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own subjects" ON public.subjects FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own subjects" ON public.subjects FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own subjects" ON public.subjects FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own subjects" ON public.subjects FOR DELETE USING (auth.uid() = user_id);

-- 10. Timetables
ALTER TABLE public.timetables ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own timetables" ON public.timetables FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own timetables" ON public.timetables FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own timetables" ON public.timetables FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own timetables" ON public.timetables FOR DELETE USING (auth.uid() = user_id);

-- 11. Schedule Items
ALTER TABLE public.schedule_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own schedule items" ON public.schedule_items FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own schedule items" ON public.schedule_items FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own schedule items" ON public.schedule_items FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own schedule items" ON public.schedule_items FOR DELETE USING (auth.uid() = user_id);

-- 12. Schedule Exceptions
ALTER TABLE public.schedule_exceptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own schedule exceptions" ON public.schedule_exceptions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own schedule exceptions" ON public.schedule_exceptions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own schedule exceptions" ON public.schedule_exceptions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own schedule exceptions" ON public.schedule_exceptions FOR DELETE USING (auth.uid() = user_id);

-- 13. Assignments
ALTER TABLE public.assignments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own assignments" ON public.assignments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own assignments" ON public.assignments FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own assignments" ON public.assignments FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own assignments" ON public.assignments FOR DELETE USING (auth.uid() = user_id);

-- 14. Exams
ALTER TABLE public.exams ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own exams" ON public.exams FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own exams" ON public.exams FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own exams" ON public.exams FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own exams" ON public.exams FOR DELETE USING (auth.uid() = user_id);

-- 15. Hackathons
ALTER TABLE public.hackathons ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own hackathons" ON public.hackathons FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own hackathons" ON public.hackathons FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own hackathons" ON public.hackathons FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own hackathons" ON public.hackathons FOR DELETE USING (auth.uid() = user_id);

-- 16. Certifications
ALTER TABLE public.certifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own certifications" ON public.certifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own certifications" ON public.certifications FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own certifications" ON public.certifications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own certifications" ON public.certifications FOR DELETE USING (auth.uid() = user_id);

-- 17. Internships
ALTER TABLE public.internships ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own internships" ON public.internships FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own internships" ON public.internships FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own internships" ON public.internships FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own internships" ON public.internships FOR DELETE USING (auth.uid() = user_id);

-- 18. Events
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own events" ON public.events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own events" ON public.events FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own events" ON public.events FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own events" ON public.events FOR DELETE USING (auth.uid() = user_id);

-- 19. Reminders
ALTER TABLE public.reminders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own reminders" ON public.reminders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own reminders" ON public.reminders FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own reminders" ON public.reminders FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own reminders" ON public.reminders FOR DELETE USING (auth.uid() = user_id);

-- 20. Notification Logs
ALTER TABLE public.notification_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own notification logs" ON public.notification_logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own notification logs" ON public.notification_logs FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 21. Devices
ALTER TABLE public.devices ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own devices" ON public.devices FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own devices" ON public.devices FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own devices" ON public.devices FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own devices" ON public.devices FOR DELETE USING (auth.uid() = user_id);

-- 22. Attachments
ALTER TABLE public.attachments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own attachments" ON public.attachments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own attachments" ON public.attachments FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own attachments" ON public.attachments FOR DELETE USING (auth.uid() = user_id);
