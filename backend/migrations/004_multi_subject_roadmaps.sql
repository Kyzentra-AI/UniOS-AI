-- ============================================================================
-- Migration 004: Multi-Subject Roadmap Support
-- ============================================================================

-- 1. Add subject and syllabus_id to roadmaps table
ALTER TABLE public.roadmaps
ADD COLUMN IF NOT EXISTS subject VARCHAR(255) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS syllabus_id UUID REFERENCES public.syllabus_documents(id) ON DELETE SET NULL;

-- 2. Create index on roadmaps for fast subject lookups
CREATE INDEX IF NOT EXISTS idx_roadmaps_learner_scope_subject 
ON public.roadmaps(learner_id, scope, subject, status);

-- 3. Create index on missions for roadmap and subject filtering
CREATE INDEX IF NOT EXISTS idx_missions_roadmap_subject 
ON public.missions(roadmap_id, subject);

-- 4. Comment on columns for clarity
COMMENT ON COLUMN public.roadmaps.subject IS 'Target subject name if subject-specific roadmap; NULL if master cross-subject roadmap';
COMMENT ON COLUMN public.roadmaps.syllabus_id IS 'Foreign key linking the roadmap to the source confirmed syllabus document';

