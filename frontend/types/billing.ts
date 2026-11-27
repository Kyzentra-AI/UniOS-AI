
export type PlanTier = 'FREE' | 'BASIC' | 'PRO';

export type BillingCycle = 'WEEKLY' | 'MONTHLY' | 'SEMESTER';

export type RenewalPolicy = 'NONE' | 'ONE_TIME' | 'MANUAL';

export type SubscriptionSource =
  | 'FREE_DEFAULT'
  | 'PAYMENT'
  | 'TRIAL'
  | 'ADMIN_PROMO'
  | 'INSTITUTIONAL';

export type EntitlementStatus = 'ACTIVE' | 'EXPIRED' | 'TRIAL';

export type OrderStatus =
  | 'PENDING'
  | 'SUCCESS'
  | 'FAILED'
  | 'ABANDONED';

export type CheckoutActionType = 'NEW' | 'RENEW' | 'UPGRADE';

export type ModuleType = 'LEARN' | 'BUILD' | 'LAUNCH';

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
  mockTests: number;
  mockTestsPeriod: string;
  mockInterviews: number;
  mockInterviewsPeriod: string;
  monthlyCredits: number;
  moduleCredits: Record<string, number>;
  projectTrackingIncluded: boolean;
  aiProjectGuidance: number;
  debuggingAccess: string;
  projectEvaluationAccess: string;
  resumeTemplateTier: string;
  githubIntegration: string;
  competeAccess: string;
  comingSoonFeatures: string[];
}

export interface PlanCycleOption {
  billingCycle: BillingCycle;
  durationDays: number;
  price: number;
  currency: string;
  gstIncluded: boolean;
  totalCredits: number;
  moduleCredits: Record<string, number>;
  mockTests: number;
  atsChecks: number;
  mockInterviews: number;
  renewalPolicy: RenewalPolicy;
}

export interface PlanConfiguration {
  planCode: PlanTier;
  name: string;
  price: number;
  currency: string;
  gstIncluded: boolean;
  durationDays: number;
  description: string;
  features: string[];
  comingSoonFeatures: string[];
  cycles: PlanCycleOption[];
  quotas: PlanQuotaMatrix;
}

export interface PlansResponse {
  plans: PlanConfiguration[];
}

export interface EntitlementResponse {
  learnerId: string;
  currentPlan: PlanTier;
  billingCycle: BillingCycle;
  status: EntitlementStatus;
  source: SubscriptionSource;
  trialUsed: boolean;
  currentPeriodStart?: string | null;
  currentPeriodEnd?: string | null;
  isActive: boolean;
  isTrial: boolean;
  daysRemaining?: number | null;
  paidAmount: number;
  renewalPolicy: RenewalPolicy;
  lastExpiredPlan?: PlanTier | null;
  creditCycleIndex: number;
  creditCycleEnd?: string | null;
  updatedAt?: string | null;
}

export interface QuotaUsageDetail {
  used: number;
  limit: number;
  remaining: number;
  period: string;
}

export interface ModuleCreditDetail {
  used: number;
  limit: number;
  remaining: number;
}

export interface CreditSummary {
  totalUsed: number;
  totalLimit: number;
  totalRemaining: number;
  cycleStart?: string | null;
  cycleEnd?: string | null;
  modules: Record<string, ModuleCreditDetail>;
}

export interface UsageResponse {
  learnerId: string;
  periodStart?: string | null;
  quotas: Record<string, QuotaUsageDetail>;
  credits?: CreditSummary | null;
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
  planCode: Exclude<PlanTier, 'FREE'>;
  billingCycle: BillingCycle;
  returnUrl?: string;
}

export interface CheckoutPreviewResponse {
  planCode: PlanTier;
  billingCycle: BillingCycle;
  actionType: CheckoutActionType;
  skuPrice: number;
  proratedCredit: number;
  remainingDaysCredited: number;
  payableAmount: number;
  currency: string;
  gstIncluded: boolean;
  newPeriodStart: string;
  newPeriodEnd: string;
  allowed: boolean;
  blockReason?: string | null;
}

export interface CheckoutResponse {
  orderId: string;
  paymentSessionId: string;
  environment: string;
  amount: number;
  currency: string;
  planCode: PlanTier;
  billingCycle: BillingCycle;
  skuPrice?: number | null;
  proratedCredit: number;
  gstIncluded: boolean;
  actionType: CheckoutActionType;
}

export interface PaymentStatusResponse {
  orderId: string;
  status: OrderStatus;
  planCode: PlanTier;
  billingCycle: BillingCycle;
  amount: number;
  currency: string;
  gstIncluded: boolean;
  cashfreePaymentId?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface OrderHistoryItem {
  orderId: string;
  planCode: PlanTier;
  billingCycle: BillingCycle;
  orderType: CheckoutActionType;
  skuPrice?: number | null;
  proratedCredit: number;
  amount: number;
  currency: string;
  gstIncluded: boolean;
  status: OrderStatus;
  cashfreePaymentId?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface OrderHistoryResponse {
  orders: OrderHistoryItem[];
  total: number;
}

export interface CreditLedgerItem {
  id: string;
  module: string;
  operation: string;
  creditsDelta: number;
  status: string;
  referenceId?: string | null;
  createdAt: string;
}

export interface CreditLedgerResponse {
  entries: CreditLedgerItem[];
  total: number;
}
