-- ==============================================================================
-- Migration 007: Subscription Models V1 (Weekly/Monthly/Semester + Hybrid Credits)
-- ==============================================================================

-- 1. New ENUM types
DO $$ BEGIN
    CREATE TYPE billing_cycle AS ENUM ('WEEKLY', 'MONTHLY', 'SEMESTER');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE subscription_source AS ENUM ('FREE_DEFAULT', 'PAYMENT', 'TRIAL', 'ADMIN_PROMO', 'INSTITUTIONAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Extend billing_entitlements
ALTER TABLE public.billing_entitlements
    ADD COLUMN IF NOT EXISTS billing_cycle billing_cycle NOT NULL DEFAULT 'MONTHLY',
    ADD COLUMN IF NOT EXISTS source subscription_source NOT NULL DEFAULT 'FREE_DEFAULT',
    ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS paid_duration_days INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS last_expired_plan plan_tier NULL,
    ADD COLUMN IF NOT EXISTS assigned_by_admin_id UUID NULL,
    ADD COLUMN IF NOT EXISTS admin_note TEXT NULL;

-- 3. Extend billing_orders (all amounts GST included)
ALTER TABLE public.billing_orders
    ADD COLUMN IF NOT EXISTS billing_cycle billing_cycle NOT NULL DEFAULT 'MONTHLY',
    ADD COLUMN IF NOT EXISTS order_type VARCHAR(32) NOT NULL DEFAULT 'NEW',
    ADD COLUMN IF NOT EXISTS proration_credit NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS sku_price NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS upgraded_from_plan plan_tier NULL;

-- 4. Extend billing_usage_quotas with hybrid credit pools & monthly feature caps
ALTER TABLE public.billing_usage_quotas
    ADD COLUMN IF NOT EXISTS cycle_start TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS cycle_end TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
    ADD COLUMN IF NOT EXISTS daily_reset_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS credit_cycle_index INT NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS learn_credits_used INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS build_credits_used INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS launch_credits_used INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS mock_tests_used INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS mock_interviews_used INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS ai_project_guidance INT NOT NULL DEFAULT 0;

-- 5. Table: billing_credit_ledger
CREATE TABLE IF NOT EXISTS public.billing_credit_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID NOT NULL REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    module VARCHAR(16) NOT NULL,
    operation VARCHAR(64) NOT NULL,
    credits_delta INT NOT NULL,
    feature_col VARCHAR(64) NULL,
    legacy_col VARCHAR(64) NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'COMMITTED',
    reference_id VARCHAR(128) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_billing_credit_ledger_learner_created
    ON public.billing_credit_ledger(learner_id, created_at DESC);

ALTER TABLE public.billing_credit_ledger ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    CREATE POLICY "Users can view their own credit ledger" ON public.billing_credit_ledger
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM public.learner_profiles
                WHERE id = billing_credit_ledger.learner_id AND user_id = auth.uid()
            )
        );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE POLICY "Service role full access on billing_credit_ledger" ON public.billing_credit_ledger
        FOR ALL USING (true) WITH CHECK (true);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 6. Table: billing_admin_grants
CREATE TABLE IF NOT EXISTS public.billing_admin_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID NOT NULL REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    admin_user_id UUID NOT NULL,
    plan_code plan_tier NOT NULL,
    billing_cycle billing_cycle NOT NULL,
    duration_days INT NOT NULL,
    grant_type VARCHAR(32) NOT NULL,
    note TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_billing_admin_grants_learner
    ON public.billing_admin_grants(learner_id, created_at DESC);

ALTER TABLE public.billing_admin_grants ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    CREATE POLICY "Service role full access on billing_admin_grants" ON public.billing_admin_grants
        FOR ALL USING (true) WITH CHECK (true);
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 7. Atomic RPC: Claim billing order exactly once for fulfillment
CREATE OR REPLACE FUNCTION public.claim_billing_order_for_fulfillment(
    p_order_id VARCHAR,
    p_payment_id VARCHAR DEFAULT NULL
)
RETURNS SETOF public.billing_orders
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    UPDATE public.billing_orders
    SET
        status = 'SUCCESS',
        cashfree_payment_id = COALESCE(p_payment_id, cashfree_payment_id),
        updated_at = NOW()
    WHERE order_id = p_order_id
      AND status <> 'SUCCESS'
    RETURNING *;
END;
$$;

-- 8. Atomic RPC: Consume credits + optional feature cap & legacy counter
CREATE OR REPLACE FUNCTION public.consume_billing_quota(
    p_learner_id UUID,
    p_module VARCHAR,
    p_operation VARCHAR,
    p_credit_cost INT,
    p_total_limit INT,
    p_module_limit INT,
    p_feature_col VARCHAR DEFAULT NULL,
    p_feature_limit INT DEFAULT NULL,
    p_legacy_col VARCHAR DEFAULT NULL,
    p_reference_id VARCHAR DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_row public.billing_usage_quotas%ROWTYPE;
    v_total_used INT;
    v_module_used INT;
    v_feature_used INT := 0;
    v_ledger_id UUID;
BEGIN
    SELECT * INTO v_row
    FROM public.billing_usage_quotas
    WHERE learner_id = p_learner_id
    FOR UPDATE;

    IF NOT FOUND THEN
        INSERT INTO public.billing_usage_quotas (learner_id)
        VALUES (p_learner_id)
        ON CONFLICT (learner_id) DO NOTHING;

        SELECT * INTO v_row
        FROM public.billing_usage_quotas
        WHERE learner_id = p_learner_id
        FOR UPDATE;
    END IF;

    v_total_used := COALESCE(v_row.learn_credits_used, 0)
                  + COALESCE(v_row.build_credits_used, 0)
                  + COALESCE(v_row.launch_credits_used, 0);

    IF p_module = 'LEARN' THEN
        v_module_used := COALESCE(v_row.learn_credits_used, 0);
    ELSIF p_module = 'BUILD' THEN
        v_module_used := COALESCE(v_row.build_credits_used, 0);
    ELSIF p_module = 'LAUNCH' THEN
        v_module_used := COALESCE(v_row.launch_credits_used, 0);
    ELSE
        RETURN jsonb_build_object('allowed', false, 'reason', 'INVALID_MODULE');
    END IF;

    IF (v_module_used + p_credit_cost) > p_module_limit THEN
        RETURN jsonb_build_object(
            'allowed', false,
            'reason', 'MODULE_CREDITS_EXHAUSTED',
            'remaining_total', GREATEST(0, p_total_limit - v_total_used),
            'remaining_module', GREATEST(0, p_module_limit - v_module_used)
        );
    END IF;

    IF (v_total_used + p_credit_cost) > p_total_limit THEN
        RETURN jsonb_build_object(
            'allowed', false,
            'reason', 'TOTAL_CREDITS_EXHAUSTED',
            'remaining_total', GREATEST(0, p_total_limit - v_total_used),
            'remaining_module', GREATEST(0, p_module_limit - v_module_used)
        );
    END IF;

    IF p_feature_col IS NOT NULL AND p_feature_limit IS NOT NULL THEN
        IF p_feature_col = 'mock_tests_used' THEN
            v_feature_used := COALESCE(v_row.mock_tests_used, 0);
        ELSIF p_feature_col = 'ats_checks' THEN
            v_feature_used := COALESCE(v_row.ats_checks, 0);
        ELSIF p_feature_col = 'mock_interviews_used' THEN
            v_feature_used := COALESCE(v_row.mock_interviews_used, 0);
        ELSIF p_feature_col = 'ai_tutor_requests' THEN
            v_feature_used := COALESCE(v_row.ai_tutor_requests, 0);
        END IF;

        IF (v_feature_used + 1) > p_feature_limit THEN
            RETURN jsonb_build_object(
                'allowed', false,
                'reason', 'FEATURE_CAP_EXHAUSTED',
                'remaining_total', GREATEST(0, p_total_limit - v_total_used),
                'remaining_module', GREATEST(0, p_module_limit - v_module_used)
            );
        END IF;
    END IF;

    UPDATE public.billing_usage_quotas
    SET
        learn_credits_used = learn_credits_used + CASE WHEN p_module = 'LEARN' THEN p_credit_cost ELSE 0 END,
        build_credits_used = build_credits_used + CASE WHEN p_module = 'BUILD' THEN p_credit_cost ELSE 0 END,
        launch_credits_used = launch_credits_used + CASE WHEN p_module = 'LAUNCH' THEN p_credit_cost ELSE 0 END,
        mock_tests_used = mock_tests_used + CASE WHEN p_feature_col = 'mock_tests_used' THEN 1 ELSE 0 END,
        mock_interviews_used = mock_interviews_used + CASE WHEN p_feature_col = 'mock_interviews_used' THEN 1 ELSE 0 END,
        ats_checks = ats_checks + CASE WHEN p_feature_col = 'ats_checks' OR p_legacy_col = 'ats_checks' THEN 1 ELSE 0 END,
        ai_tutor_requests = ai_tutor_requests + CASE WHEN p_feature_col = 'ai_tutor_requests' OR p_legacy_col = 'ai_tutor_requests' THEN 1 ELSE 0 END,
        ai_roadmap_generations = ai_roadmap_generations + CASE WHEN p_legacy_col = 'ai_roadmap_generations' THEN 1 ELSE 0 END,
        practice_questions = practice_questions + CASE WHEN p_legacy_col = 'practice_questions' THEN 1 ELSE 0 END,
        resume_generations = resume_generations + CASE WHEN p_legacy_col = 'resume_generations' THEN 1 ELSE 0 END,
        ai_project_guidance = ai_project_guidance + CASE WHEN p_legacy_col = 'ai_project_guidance' THEN 1 ELSE 0 END,
        updated_at = NOW()
    WHERE learner_id = p_learner_id;

    INSERT INTO public.billing_credit_ledger (
        learner_id, module, operation, credits_delta, feature_col, legacy_col, status, reference_id
    )
    VALUES (
        p_learner_id, p_module, p_operation, p_credit_cost, p_feature_col, p_legacy_col, 'COMMITTED', p_reference_id
    )
    RETURNING id INTO v_ledger_id;

    RETURN jsonb_build_object(
        'allowed', true,
        'reason', 'OK',
        'ledger_id', v_ledger_id,
        'remaining_total', GREATEST(0, p_total_limit - (v_total_used + p_credit_cost)),
        'remaining_module', GREATEST(0, p_module_limit - (v_module_used + p_credit_cost))
    );
END;
$$;

-- 9. Atomic RPC: Refund credits on downstream AI error
CREATE OR REPLACE FUNCTION public.refund_billing_quota(
    p_ledger_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_entry public.billing_credit_ledger%ROWTYPE;
BEGIN
    SELECT * INTO v_entry
    FROM public.billing_credit_ledger
    WHERE id = p_ledger_id
      AND status = 'COMMITTED'
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    UPDATE public.billing_usage_quotas
    SET
        learn_credits_used = GREATEST(0, learn_credits_used - CASE WHEN v_entry.module = 'LEARN' THEN v_entry.credits_delta ELSE 0 END),
        build_credits_used = GREATEST(0, build_credits_used - CASE WHEN v_entry.module = 'BUILD' THEN v_entry.credits_delta ELSE 0 END),
        launch_credits_used = GREATEST(0, launch_credits_used - CASE WHEN v_entry.module = 'LAUNCH' THEN v_entry.credits_delta ELSE 0 END),
        mock_tests_used = GREATEST(0, mock_tests_used - CASE WHEN v_entry.feature_col = 'mock_tests_used' THEN 1 ELSE 0 END),
        mock_interviews_used = GREATEST(0, mock_interviews_used - CASE WHEN v_entry.feature_col = 'mock_interviews_used' THEN 1 ELSE 0 END),
        ats_checks = GREATEST(0, ats_checks - CASE WHEN v_entry.feature_col = 'ats_checks' OR v_entry.legacy_col = 'ats_checks' THEN 1 ELSE 0 END),
        ai_tutor_requests = GREATEST(0, ai_tutor_requests - CASE WHEN v_entry.feature_col = 'ai_tutor_requests' OR v_entry.legacy_col = 'ai_tutor_requests' THEN 1 ELSE 0 END),
        ai_roadmap_generations = GREATEST(0, ai_roadmap_generations - CASE WHEN v_entry.legacy_col = 'ai_roadmap_generations' THEN 1 ELSE 0 END),
        practice_questions = GREATEST(0, practice_questions - CASE WHEN v_entry.legacy_col = 'practice_questions' THEN 1 ELSE 0 END),
        resume_generations = GREATEST(0, resume_generations - CASE WHEN v_entry.legacy_col = 'resume_generations' THEN 1 ELSE 0 END),
        ai_project_guidance = GREATEST(0, ai_project_guidance - CASE WHEN v_entry.legacy_col = 'ai_project_guidance' THEN 1 ELSE 0 END),
        updated_at = NOW()
    WHERE learner_id = v_entry.learner_id;

    UPDATE public.billing_credit_ledger
    SET status = 'REFUNDED'
    WHERE id = p_ledger_id;

    RETURN TRUE;
END;
$$;

