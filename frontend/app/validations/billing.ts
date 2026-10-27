
import { z } from 'zod';

const planTierSchema = z.enum(['FREE', 'BASIC', 'PRO']);

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
  projectTrackingIncluded: z.boolean(),
  aiProjectGuidance: z.number(),
  competeAccess: z.string(),
});

const planConfigurationSchema = z.object({
  planCode: planTierSchema,
  name: z.string(),
  price: z.number(),
  currency: z.string(),
  durationDays: z.number(),
  description: z.string(),
  features: z.array(z.string()),
  quotas: planQuotaMatrixSchema,
});

export const plansResponseSchema = z.object({
  plans: z.array(planConfigurationSchema),
});

export const entitlementResponseSchema = z.object({
  learnerId: z.string(),
  currentPlan: planTierSchema,
  status: entitlementStatusSchema,
  trialUsed: z.boolean(),
  currentPeriodStart: z.string().nullable().optional(),
  currentPeriodEnd: z.string().nullable().optional(),
  isActive: z.boolean(),
  isTrial: z.boolean(),
  daysRemaining: z.number().nullable().optional(),
  updatedAt: z.string().nullable().optional(),
});

const quotaUsageDetailSchema = z.object({
  used: z.number(),
  limit: z.number(),
  remaining: z.number(),
  period: z.string(),
});

export const usageResponseSchema = z.object({
  learnerId: z.string(),
  periodStart: z.string().nullable().optional(),
  quotas: z.record(z.string(), quotaUsageDetailSchema),
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
  planCode: planTierSchema,
  returnUrl: z.string().url().optional(),
});

export const checkoutResponseSchema = z.object({
  orderId: z.string(),
  paymentSessionId: z.string(),
  environment: z.string(),
  amount: z.number(),
  currency: z.string(),
  planCode: planTierSchema,
});

export const paymentStatusResponseSchema = z.object({
  orderId: z.string(),
  status: orderStatusSchema,
  planCode: planTierSchema,
  amount: z.number(),
  currency: z.string(),
  cashfreePaymentId: z.string().nullable().optional(),
  createdAt: z.string().nullable().optional(),
  updatedAt: z.string().nullable().optional(),
});

const orderHistoryItemSchema = z.object({
  orderId: z.string(),
  planCode: planTierSchema,
  amount: z.number(),
  currency: z.string(),
  status: orderStatusSchema,
  cashfreePaymentId: z.string().nullable().optional(),
  createdAt: z.string().nullable().optional(),
  updatedAt: z.string().nullable().optional(),
});

export const orderHistoryResponseSchema = z.object({
  orders: z.array(orderHistoryItemSchema),
  total: z.number(),
});
