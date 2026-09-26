-- Create the public.users table that extends auth.users
CREATE TABLE IF NOT EXISTS public.users (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    terms_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    failed_login_attempts INT DEFAULT 0,
    account_locked_until TIMESTAMP WITH TIME ZONE NULL,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE NULL
);

-- Enable Row Level Security (RLS) on public.users
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Allow users to read their own profile
CREATE POLICY "Users can view their own profile" 
ON public.users 
FOR SELECT 
USING (auth.uid() = user_id);

-- Allow service_role (backend admin) to do everything
CREATE POLICY "Service role has full access" 
ON public.users 
FOR ALL 
USING (true) 
WITH CHECK (true);

-- Trigger to automatically create a public.users profile on auth signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (
        user_id, 
        full_name, 
        email, 
        terms_accepted, 
        email_verified
    )
    VALUES (
        new.id,
        COALESCE(new.raw_user_meta_data->>'full_name', ''),
        new.email,
        COALESCE((new.raw_user_meta_data->>'terms_accepted')::boolean, false),
        false
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recreate trigger for user creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Trigger to update email verification and email when updated in auth.users
CREATE OR REPLACE FUNCTION public.handle_user_update()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.users
    SET 
        email_verified = (new.email_confirmed_at IS NOT NULL),
        email = new.email
    WHERE user_id = new.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recreate trigger for user update
DROP TRIGGER IF EXISTS on_auth_user_updated ON auth.users;
CREATE TRIGGER on_auth_user_updated
    AFTER UPDATE OF email_confirmed_at, email ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_user_update();


-- ==============================================================================
-- EPIC 2: SPRINT 2 - UNIVERSAL LEARNER PROFILE & ONBOARDING
-- ==============================================================================

-- 1. Learner Profiles Table
CREATE TABLE IF NOT EXISTS public.learner_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES public.users(user_id) ON DELETE CASCADE,
    primary_goal VARCHAR(255),
    target_skills JSONB DEFAULT '[]'::jsonb,
    skills JSONB DEFAULT '[]'::jsonb,
    projects JSONB DEFAULT '[]'::jsonb,
    research TEXT,
    experience TEXT,
    onboarding_status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    onboarding_version INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.learner_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own learner profile" ON public.learner_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own learner profile" ON public.learner_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own learner profile" ON public.learner_profiles
    FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role full access on learner_profiles" ON public.learner_profiles
    FOR ALL USING (true) WITH CHECK (true);


-- 2. Academic Profiles Table
CREATE TABLE IF NOT EXISTS public.academic_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_profile_id UUID UNIQUE REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    academic_status VARCHAR(50), -- BACHELOR, MASTER, RECENT_GRADUATE
    university VARCHAR(255),
    degree_program VARCHAR(255),
    domain VARCHAR(255),
    current_year VARCHAR(50),
    graduation_year INT,
    subjects JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.academic_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own academic profile" ON public.academic_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = academic_profiles.learner_profile_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own academic profile" ON public.academic_profiles
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_profile_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own academic profile" ON public.academic_profiles
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = academic_profiles.learner_profile_id AND user_id = auth.uid()
        )
    ) WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_profile_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on academic_profiles" ON public.academic_profiles
    FOR ALL USING (true) WITH CHECK (true);


-- 3. Learning Preferences Table
CREATE TABLE IF NOT EXISTS public.learning_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_profile_id UUID UNIQUE REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    daily_study_hours VARCHAR(50), -- LESS_THAN_1, 1_2, 2_3, 3_4, 4_PLUS
    learning_depth VARCHAR(50), -- QUICK, BALANCED, DEEP
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.learning_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own learning preferences" ON public.learning_preferences
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learning_preferences.learner_profile_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own learning preferences" ON public.learning_preferences
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_profile_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own learning preferences" ON public.learning_preferences
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learning_preferences.learner_profile_id AND user_id = auth.uid()
        )
    ) WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_profile_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on learning_preferences" ON public.learning_preferences
    FOR ALL USING (true) WITH CHECK (true);

-- ==============================================================================
-- KIE INTEGRATION EXTENSIONS
-- ==============================================================================

ALTER TABLE public.learner_profiles
ADD COLUMN IF NOT EXISTS pending_kie_questions JSONB DEFAULT NULL,
ADD COLUMN IF NOT EXISTS inferred_context JSONB DEFAULT '{}'::jsonb;

-- ==============================================================================
-- EPIC 3: SPRINT 3 - SYLLABUS, ROADMAPS, MISSIONS, EVENTS
-- ==============================================================================

-- 1. Syllabus Documents Table
CREATE TABLE IF NOT EXISTS public.syllabus_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    storage_key VARCHAR(512) NOT NULL,
    file_type VARCHAR(50) DEFAULT 'application/pdf',
    status VARCHAR(50) DEFAULT 'PROCESSING', -- PROCESSING, WAITING_FOR_CONFIRMATION, CONFIRMED, FAILED
    version INT DEFAULT 1,
    parsed_content JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.syllabus_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own syllabus" ON public.syllabus_documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = syllabus_documents.learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own syllabus" ON public.syllabus_documents
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own syllabus" ON public.syllabus_documents
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = syllabus_documents.learner_id AND user_id = auth.uid()
        )
    ) WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on syllabus_documents" ON public.syllabus_documents
    FOR ALL USING (true) WITH CHECK (true);


-- 2. Roadmaps Table
CREATE TABLE IF NOT EXISTS public.roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    version INT DEFAULT 1,
    scope VARCHAR(50) NOT NULL, -- ACADEMIC, CAREER, BOTH
    status VARCHAR(50) DEFAULT 'ACTIVE', -- ACTIVE, INACTIVE
    plan_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.roadmaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own roadmaps" ON public.roadmaps
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = roadmaps.learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own roadmaps" ON public.roadmaps
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own roadmaps" ON public.roadmaps
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = roadmaps.learner_id AND user_id = auth.uid()
        )
    ) WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on roadmaps" ON public.roadmaps
    FOR ALL USING (true) WITH CHECK (true);


-- 3. Missions Table
CREATE TABLE IF NOT EXISTS public.missions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID REFERENCES public.roadmaps(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    mission_type VARCHAR(50) NOT NULL, -- LEARNING, REVISION, ASSIGNMENT, PRACTICAL, ARTIFACT, CAREER
    subject VARCHAR(255),
    priority VARCHAR(50),
    estimated_minutes INT,
    week INT,
    sequence INT,
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, COMPLETED, DEFERRED, SKIPPED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.missions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own missions" ON public.missions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.roadmaps 
            JOIN public.learner_profiles ON roadmaps.learner_id = learner_profiles.id
            WHERE roadmaps.id = missions.roadmap_id AND learner_profiles.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own missions" ON public.missions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.roadmaps 
            JOIN public.learner_profiles ON roadmaps.learner_id = learner_profiles.id
            WHERE roadmaps.id = roadmap_id AND learner_profiles.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own missions" ON public.missions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.roadmaps 
            JOIN public.learner_profiles ON roadmaps.learner_id = learner_profiles.id
            WHERE roadmaps.id = missions.roadmap_id AND learner_profiles.user_id = auth.uid()
        )
    ) WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.roadmaps 
            JOIN public.learner_profiles ON roadmaps.learner_id = learner_profiles.id
            WHERE roadmaps.id = roadmap_id AND learner_profiles.user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on missions" ON public.missions
    FOR ALL USING (true) WITH CHECK (true);


-- 4. Learner Events Table
CREATE TABLE IF NOT EXISTS public.learner_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL, -- e.g., SYLLABUS_CONFIRMED, MISSION_COMPLETED
    entity_type VARCHAR(100) NOT NULL, -- e.g., SYLLABUS, MISSION
    entity_id UUID NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.learner_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own events" ON public.learner_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_events.learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own events" ON public.learner_events
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on learner_events" ON public.learner_events
    FOR ALL USING (true) WITH CHECK (true);


