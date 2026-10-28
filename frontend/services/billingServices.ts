
import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import {
  checkoutResponseSchema,
  entitlementResponseSchema,
  orderHistoryResponseSchema,
  paymentStatusResponseSchema,
  plansResponseSchema,
  trialActivationResponseSchema,
  usageResponseSchema,
} from '@/app/validations/billing';

import type {
  CheckoutRequest,
  CheckoutResponse,
  EntitlementResponse,
  OrderHistoryResponse,
  PaymentStatusResponse,
  PlansResponse,
  TrialActivationResponse,
  UsageResponse,
} from '@/types/billing';

function getAuthHeaders(): HeadersInit {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error(
      'Authentication required. Please log in again.'
    );
  }

  return {
    Authorization: `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  };
}

export async function getBillingPlans(): Promise<PlansResponse> {
  const response = await apiRequest<PlansResponse>(
    '/api/v1/billing/plans',
    {
      method: 'GET',
    }
  );

  return plansResponseSchema.parse(response);
}

export async function getMyEntitlement(): Promise<EntitlementResponse> {
  const response = await apiRequest<EntitlementResponse>(
    '/api/v1/billing/me',
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  return entitlementResponseSchema.parse(response);
}

export async function getMyUsage(): Promise<UsageResponse> {
  const response = await apiRequest<UsageResponse>(
    '/api/v1/billing/usage',
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  return usageResponseSchema.parse(response);
}

export async function activateBillingTrial(): Promise<TrialActivationResponse> {
  const response = await apiRequest<TrialActivationResponse>(
    '/api/v1/billing/trial',
    {
      method: 'POST',
      headers: getAuthHeaders(),
    }
  );

  return trialActivationResponseSchema.parse(response);
}

export async function createBillingCheckout(
  payload: CheckoutRequest
): Promise<CheckoutResponse> {
  const response = await apiRequest<CheckoutResponse>(
    '/api/v1/billing/checkout',
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    }
  );

  return checkoutResponseSchema.parse(response);
}

export async function renewBillingSubscription(
  payload: CheckoutRequest
): Promise<CheckoutResponse> {
  const response = await apiRequest<CheckoutResponse>(
    '/api/v1/billing/renew',
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    }
  );

  return checkoutResponseSchema.parse(response);
}

export async function verifyBillingPayment(
  orderId: string
): Promise<PaymentStatusResponse> {
  const response = await apiRequest<PaymentStatusResponse>(
    `/api/v1/billing/payments/${encodeURIComponent(orderId)}`,
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  return paymentStatusResponseSchema.parse(response);
}

export async function getBillingHistory(): Promise<OrderHistoryResponse> {
  const response = await apiRequest<OrderHistoryResponse>(
    '/api/v1/billing/history',
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  return orderHistoryResponseSchema.parse(response);
}
