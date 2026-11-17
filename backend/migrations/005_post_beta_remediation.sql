-- ============================================================================
-- POST-BETA & WEBSITE TESTING BACKEND REMEDIATION MIGRATION (IDEMPOTENT)
-- ============================================================================

-- 1. Ensure syllabus_documents tracks subject and file hash for fast caching (PERF-03 & CONTENT-11)
ALTER TABLE public.syllabus_documents
  ADD COLUMN IF NOT EXISTS subject VARCHAR(255) NULL,
  ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64) NULL,
  ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

CREATE INDEX IF NOT EXISTS idx_syllabus_docs_learner_subject
  ON public.syllabus_documents (learner_id, subject, is_active);

-- 2. Ensure learning_sessions tracks subject & syllabus_id for Mentor & Assessment grounding (Web BUG-05, CONTENT-09)
ALTER TABLE public.learning_sessions
  ADD COLUMN IF NOT EXISTS subject VARCHAR(255) NULL,
  ADD COLUMN IF NOT EXISTS syllabus_id UUID NULL REFERENCES public.syllabus_documents(id) ON DELETE SET NULL;

-- 3. Ensure assessment_attempts indexes learner_id + topic for fast retake deduplication (Beta BUG-01)
CREATE INDEX IF NOT EXISTS idx_assessment_attempts_learner_topic
  ON public.assessment_attempts (learner_id, topic, is_completed);

