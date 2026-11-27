
import { z } from 'zod';

const planTierSchema = z.enum(['FREE', 'BASIC', 'PRO']);

const billingCycleSchema = z.enum([
  'WEEKLY',
  'MONTHLY',
  'SEMESTER',
]);

const renewalPolicySchema = z.enum([
  'NONE',
  'ONE_TIME',
  'MANUAL',
]);

const subscriptionSourceSchema = z.enum([
  'FREE_DEFAULT',
  'PAYMENT',
  'TRIAL',
  'ADMIN_PROMO',
  'INSTITUTIONAL',
]);

const entitlementStatusSchema = z.enum([
  'ACTIVE',
  'EXPIRED',
  'TRIAL',
]);

const orderStatusSchema = z.enum([
  'PENDING',
  'SUCCESS',
  'FAILED',
  'ABANDONED',
]);

const actionTypeSchema = z.enum([
  'NEW',
  'RENEW',
  'UPGRADE',
]);

const planQuotaMatrixSchema = z.object({
  aiRoadmapGenerations: z.number(),
  aiRoadmapPeriod: z.string(),
  aiTutorRequests: z.number(),
  aiTutorPeriod: z.string(),
  practiceQuestions: z.number(),
  practiceQuestionsPeriod: z.string(),
  resumeGenerations: z.number(),
  resumeGenerationsPeriod: z.string(),
  atsChecks: z.number(),
  atsChecksPeriod: z.string(),
  mockTests: z.number(),
  mockTestsPeriod: z.string(),
  mockInterviews: z.number(),
  mockInterviewsPeriod: z.string(),
  monthlyCredits: z.number(),
  moduleCredits: z.record(z.string(), z.number()),
  projectTrackingIncluded: z.boolean(),
  aiProjectGuidance: z.number(),
  debuggingAccess: z.string(),
  projectEvaluationAccess: z.string(),
  resumeTemplateTier: z.string(),
  githubIntegration: z.string(),
  competeAccess: z.string(),
  comingSoonFeatures: z.array(z.string()),
});

const planCycleOptionSchema = z.object({
  billingCycle: billingCycleSchema,
  durationDays: z.number(),
  price: z.number(),
  currency: z.string(),
  gstIncluded: z.boolean(),
  totalCredits: z.number(),
  moduleCredits: z.record(z.string(), z.number()),
  mockTests: z.number(),
  atsChecks: z.number(),
  mockInterviews: z.number(),
  renewalPolicy: renewalPolicySchema,
});

const planConfigurationSchema = z.object({
  planCode: planTierSchema,
  name: z.string(),
  price: z.number(),
  currency: z.string(),
  gstIncluded: z.boolean(),
  durationDays: z.number(),
  description: z.string(),
  features: z.array(z.string()),
  comingSoonFeatures: z.array(z.string()),
  cycles: z.array(planCycleOptionSchema),
  quotas: planQuotaMatrixSchema,
});

export const plansResponseSchema = z.object({
  plans: z.array(planConfigurationSchema),
});

export const entitlementResponseSchema = z.object({
  learnerId: z.string(),
  currentPlan: planTierSchema,
  billingCycle: billingCycleSchema,
  status: entitlementStatusSchema,
  source: subscriptionSourceSchema,
  trialUsed: z.boolean(),
  currentPeriodStart: z.string().nullable().optional(),
  currentPeriodEnd: z.string().nullable().optional(),
  isActive: z.boolean(),
  isTrial: z.boolean(),
  daysRemaining: z.number().nullable().optional(),
  paidAmount: z.number(),
  renewalPolicy: renewalPolicySchema,
  lastExpiredPlan: planTierSchema.nullable().optional(),
  creditCycleIndex: z.number(),
  creditCycleEnd: z.string().nullable().optional(),
  updatedAt: z.string().nullable().optional(),
});

const quotaUsageDetailSchema = z.object({
  used: z.number(),
  limit: z.number(),
  remaining: z.number(),
  period: z.string(),
});

const moduleCreditDetailSchema = z.object({
  used: z.number(),
  limit: z.number(),
  remaining: z.number(),
});

const creditSummarySchema = z.object({
  totalUsed: z.number(),
  totalLimit: z.number(),
  totalRemaining: z.number(),
  cycleStart: z.string().nullable().optional(),
  cycleEnd: z.string().nullable().optional(),
  modules: z.record(z.string(), moduleCreditDetailSchema),
});

export const usageResponseSchema = z.object({
  learnerId: z.string(),
  periodStart: z.string().nullable().optional(),
  quotas: z.record(z.string(), quotaUsageDetailSchema),
  credits: creditSummarySchema.nullable().optional(),
  nextResetDaily: z.string(),
  nextResetMonthly: z.string(),
  updatedAt: z.string().nullable().optional(),
});

export const trialActivationResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  entitlement: entitlementResponseSchema,
});

export const checkoutRequestSchema = z.object({
  planCode: z.enum(['BASIC', 'PRO']),
  billingCycle: billingCycleSchema,
  returnUrl: z.string().url().optional(),
});

export const checkoutPreviewResponseSchema = z.object({
  planCode: planTierSchema,
  billingCycle: billingCycleSchema,
  actionType: actionTypeSchema,
  skuPrice: z.number(),
  proratedCredit: z.number(),
  remainingDaysCredited: z.number(),
  payableAmount: z.number(),
  currency: z.string(),
  gstIncluded: z.boolean(),
  newPeriodStart: z.string(),
  newPeriodEnd: z.string(),
  allowed: z.boolean(),
  blockReason: z.string().nullable().optional(),
});

export const checkoutResponseSchema = z.object({
  orderId: z.string(),
  paymentSessionId: z.string(),
  environment: z.string(),
  amount: z.number(),
  currency: z.string(),
  planCode: planTierSchema,
  billingCycle: billingCycleSchema,
  skuPrice: z.number().nullable().optional(),
  proratedCredit: z.number(),
  gstIncluded: z.boolean(),
  actionType: actionTypeSchema,
});

export const paymentStatusResponseSchema = z.object({
  orderId: z.string(),
  status: orderStatusSchema,
  planCode: planTierSchema,
  billingCycle: billingCycleSchema,
  amount: z.number(),
  currency: z.string(),
  gstIncluded: z.boolean(),
  cashfreePaymentId: z.string().nullable().optional(),
  createdAt: z.string().nullable().optional(),
  updatedAt: z.string().nullable().optional(),
});

const orderHistoryItemSchema = z.object({
  orderId: z.string(),
  planCode: planTierSchema,
  billingCycle: billingCycleSchema,
  orderType: actionTypeSchema,
  skuPrice: z.number().nullable().optional(),
  proratedCredit: z.number(),
  amount: z.number(),
  currency: z.string(),
  gstIncluded: z.boolean(),
  status: orderStatusSchema,
  cashfreePaymentId: z.string().nullable().optional(),
  createdAt: z.string().nullable().optional(),
  updatedAt: z.string().nullable().optional(),
});

export const orderHistoryResponseSchema = z.object({
  orders: z.array(orderHistoryItemSchema),
  total: z.number(),
});

const creditLedgerItemSchema = z.object({
  id: z.string(),
  module: z.string(),
  operation: z.string(),
  creditsDelta: z.number(),
  status: z.string(),
  referenceId: z.string().nullable().optional(),
  createdAt: z.string(),
});

export const creditLedgerResponseSchema = z.object({
  entries: z.array(creditLedgerItemSchema),
  total: z.number(),
});
