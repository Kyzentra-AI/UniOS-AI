-- ==============================================================================
-- EPIC 9: ASSESSMENTS REPOSITORY & MENTOR CHAT CONVERSATIONS
-- ==============================================================================

-- 1. Table: assessments (Persisted assessments per session & topic)
CREATE TABLE IF NOT EXISTS public.assessments (
    id VARCHAR(64) PRIMARY KEY,
    session_id UUID REFERENCES public.learning_sessions(id) ON DELETE CASCADE,
    learner_id UUID REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    topic VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'mcq',
    instructions TEXT,
    questions JSONB NOT NULL DEFAULT '[]'::jsonb,
    answer_keys JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_assessments_session_topic ON public.assessments(session_id, topic);
CREATE INDEX IF NOT EXISTS idx_assessments_learner_id ON public.assessments(learner_id);

ALTER TABLE public.assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own assessments" ON public.assessments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = assessments.learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on assessments" ON public.assessments
    FOR ALL USING (true) WITH CHECK (true);


-- 2. Table: mentor_conversations
CREATE TABLE IF NOT EXISTS public.mentor_conversations (
    id VARCHAR(64) PRIMARY KEY,
    learner_id UUID NOT NULL REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    mode VARCHAR(50) NOT NULL DEFAULT 'tutor',
    context JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mentor_conversations_learner_id ON public.mentor_conversations(learner_id);

ALTER TABLE public.mentor_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own mentor conversations" ON public.mentor_conversations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = mentor_conversations.learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on mentor_conversations" ON public.mentor_conversations
    FOR ALL USING (true) WITH CHECK (true);


-- 3. Table: mentor_messages
CREATE TABLE IF NOT EXISTS public.mentor_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(64) NOT NULL REFERENCES public.mentor_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mentor_messages_conv_id ON public.mentor_messages(conversation_id);

ALTER TABLE public.mentor_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own mentor messages" ON public.mentor_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.mentor_conversations mc
            JOIN public.learner_profiles lp ON mc.learner_id = lp.id
            WHERE mc.id = mentor_messages.conversation_id AND lp.user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on mentor_messages" ON public.mentor_messages
    FOR ALL USING (true) WITH CHECK (true);
