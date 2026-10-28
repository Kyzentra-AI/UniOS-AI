-- ==============================================================================
-- EPIC 8: SUBSCRIPTION MODEL & CASHFREE INTEGRATION MIGRATION
-- ==============================================================================

-- 1. Create ENUM types safely if they do not exist
DO $$ BEGIN
    CREATE TYPE plan_tier AS ENUM ('FREE', 'BASIC', 'PRO');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE entitlement_status AS ENUM ('ACTIVE', 'EXPIRED', 'TRIAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE order_status AS ENUM ('PENDING', 'SUCCESS', 'FAILED', 'ABANDONED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Table: billing_entitlements
CREATE TABLE IF NOT EXISTS public.billing_entitlements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID UNIQUE NOT NULL REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    current_plan plan_tier NOT NULL DEFAULT 'FREE',
    status entitlement_status NOT NULL DEFAULT 'ACTIVE',
    trial_used BOOLEAN NOT NULL DEFAULT FALSE,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table: billing_usage_quotas
CREATE TABLE IF NOT EXISTS public.billing_usage_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID UNIQUE NOT NULL REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    period_start TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ai_roadmap_generations INT NOT NULL DEFAULT 0,
    ai_tutor_requests INT NOT NULL DEFAULT 0,
    practice_questions INT NOT NULL DEFAULT 0,
    resume_generations INT NOT NULL DEFAULT 0,
    ats_checks INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Table: billing_orders
CREATE TABLE IF NOT EXISTS public.billing_orders (
    order_id VARCHAR(64) PRIMARY KEY,
    learner_id UUID NOT NULL REFERENCES public.learner_profiles(id) ON DELETE CASCADE,
    plan_code plan_tier NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    status order_status NOT NULL DEFAULT 'PENDING',
    cashfree_payment_id VARCHAR(128) NULL,
    payment_session_id VARCHAR(255) NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Indexes
CREATE INDEX IF NOT EXISTS idx_billing_entitlements_learner_id ON public.billing_entitlements(learner_id);
CREATE INDEX IF NOT EXISTS idx_billing_usage_quotas_learner_id ON public.billing_usage_quotas(learner_id);
CREATE INDEX IF NOT EXISTS idx_billing_orders_learner_id ON public.billing_orders(learner_id);
CREATE INDEX IF NOT EXISTS idx_billing_orders_status ON public.billing_orders(status);

-- 6. Row-Level Security (RLS) Configuration

-- Enable RLS
ALTER TABLE public.billing_entitlements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_usage_quotas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_orders ENABLE ROW LEVEL SECURITY;

-- billing_entitlements policies
CREATE POLICY "Users can view their own entitlements" ON public.billing_entitlements
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = billing_entitlements.learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on billing_entitlements" ON public.billing_entitlements
    FOR ALL USING (true) WITH CHECK (true);

-- billing_usage_quotas policies
CREATE POLICY "Users can view their own usage quotas" ON public.billing_usage_quotas
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = billing_usage_quotas.learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on billing_usage_quotas" ON public.billing_usage_quotas
    FOR ALL USING (true) WITH CHECK (true);

-- billing_orders policies
CREATE POLICY "Users can view their own billing orders" ON public.billing_orders
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.learner_profiles 
            WHERE id = billing_orders.learner_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access on billing_orders" ON public.billing_orders
    FOR ALL USING (true) WITH CHECK (true);
