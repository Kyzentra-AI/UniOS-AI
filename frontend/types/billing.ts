
export type PlanTier = 'FREE' | 'BASIC' | 'PRO';

export type EntitlementStatus = 'ACTIVE' | 'EXPIRED' | 'TRIAL';

export type OrderStatus =
  | 'PENDING'
  | 'SUCCESS'
  | 'FAILED'
  | 'ABANDONED';

export interface PlanQuotaMatrix {
  aiRoadmapGenerations: number;
  aiRoadmapPeriod: string;
  aiTutorRequests: number;
  aiTutorPeriod: string;
  practiceQuestions: number;
  practiceQuestionsPeriod: string;
  resumeGenerations: number;
  resumeGenerationsPeriod: string;
  atsChecks: number;
  atsChecksPeriod: string;
  projectTrackingIncluded: boolean;
  aiProjectGuidance: number;
  competeAccess: string;
}

export interface PlanConfiguration {
  planCode: PlanTier;
  name: string;
  price: number;
  currency: string;
  durationDays: number;
  description: string;
  features: string[];
  quotas: PlanQuotaMatrix;
}

export interface PlansResponse {
  plans: PlanConfiguration[];
}

export interface EntitlementResponse {
  learnerId: string;
  currentPlan: PlanTier;
  status: EntitlementStatus;
  trialUsed: boolean;
  currentPeriodStart?: string | null;
  currentPeriodEnd?: string | null;
  isActive: boolean;
  isTrial: boolean;
  daysRemaining?: number | null;
  updatedAt?: string | null;
}

export interface QuotaUsageDetail {
  used: number;
  limit: number;
  remaining: number;
  period: string;
}

export interface UsageResponse {
  learnerId: string;
  periodStart?: string | null;
  quotas: Record<string, QuotaUsageDetail>;
  nextResetDaily: string;
  nextResetMonthly: string;
  updatedAt?: string | null;
}

export interface TrialActivationResponse {
  success: boolean;
  message: string;
  entitlement: EntitlementResponse;
}

export interface CheckoutRequest {
  planCode: PlanTier;
  returnUrl?: string;
}

export interface CheckoutResponse {
  orderId: string;
  paymentSessionId: string;
  environment: string;
  amount: number;
  currency: string;
  planCode: PlanTier;
}

export interface PaymentStatusResponse {
  orderId: string;
  status: OrderStatus;
  planCode: PlanTier;
  amount: number;
  currency: string;
  cashfreePaymentId?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface OrderHistoryItem {
  orderId: string;
  planCode: PlanTier;
  amount: number;
  currency: string;
  status: OrderStatus;
  cashfreePaymentId?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface OrderHistoryResponse {
  orders: OrderHistoryItem[];
  total: number;
}
