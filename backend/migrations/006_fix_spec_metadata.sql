-- ============================================================================
-- Migration 006: Consolidated Fix Spec Metadata & Ordering Support
-- ============================================================================

-- 1. Add structured mission metadata and curriculum hierarchy columns
ALTER TABLE public.missions
  ADD COLUMN IF NOT EXISTS chapter VARCHAR(255) NULL,
  ADD COLUMN IF NOT EXISTS topic VARCHAR(255) NULL,
  ADD COLUMN IF NOT EXISTS objectives TEXT NULL,
  ADD COLUMN IF NOT EXISTS core_concepts TEXT NULL,
  ADD COLUMN IF NOT EXISTS deliverables TEXT NULL,
  ADD COLUMN IF NOT EXISTS mastery_criteria TEXT NULL;

-- 2. Index for deterministic week + sequence ordering
CREATE INDEX IF NOT EXISTS idx_missions_roadmap_week_seq
  ON public.missions (roadmap_id, week, sequence);

