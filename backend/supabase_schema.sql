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
-- EPIC 2: CORE IDENTITY, STUDENT PROFILE & AI MEMORY SYSTEM
-- ==============================================================================

-- 1. Student Profiles Table
CREATE TABLE IF NOT EXISTS public.student_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES public.users(user_id) ON DELETE CASCADE,
    degree_program VARCHAR(150) NOT NULL,
    academic_year VARCHAR(50) NOT NULL,
    primary_language VARCHAR(50) NOT NULL DEFAULT 'English',
    preferred_modes TEXT[] DEFAULT ARRAY['Visual Diagrams'],
    primary_career_goal VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS for Student Profiles
ALTER TABLE public.student_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own student profile" ON public.student_profiles
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own student profile" ON public.student_profiles
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own student profile" ON public.student_profiles
    FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own student profile" ON public.student_profiles
    FOR DELETE
    USING (auth.uid() = user_id);

-- Service role full access
CREATE POLICY "Service role full access on student_profiles" ON public.student_profiles
    FOR ALL USING (true) WITH CHECK (true);


-- 2. AI Implicit Memory Logs Table
CREATE TABLE IF NOT EXISTS public.ai_implicit_memory_logs (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(user_id) ON DELETE CASCADE,
    concept VARCHAR(100) NOT NULL,
    error_frequency INT DEFAULT 1,
    last_observed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE
);

-- Enable RLS for Memory Logs
ALTER TABLE public.ai_implicit_memory_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own memory logs" ON public.ai_implicit_memory_logs
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own memory logs" ON public.ai_implicit_memory_logs
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own memory logs" ON public.ai_implicit_memory_logs
    FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own memory logs" ON public.ai_implicit_memory_logs
    FOR DELETE
    USING (auth.uid() = user_id);

-- Service role full access
CREATE POLICY "Service role full access on ai_implicit_memory_logs" ON public.ai_implicit_memory_logs
    FOR ALL USING (true) WITH CHECK (true);


-- 3. AI Explicit Directives Table (User custom rules)
CREATE TABLE IF NOT EXISTS public.ai_explicit_directives (
    directive_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(user_id) ON DELETE CASCADE,
    directive_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS for Explicit Directives
ALTER TABLE public.ai_explicit_directives ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own explicit directives" ON public.ai_explicit_directives
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own explicit directives" ON public.ai_explicit_directives
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own explicit directives" ON public.ai_explicit_directives
    FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own explicit directives" ON public.ai_explicit_directives
    FOR DELETE
    USING (auth.uid() = user_id);

-- Service role full access
CREATE POLICY "Service role full access on ai_explicit_directives" ON public.ai_explicit_directives
    FOR ALL USING (true) WITH CHECK (true);

