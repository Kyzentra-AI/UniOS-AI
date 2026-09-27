import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import type {
  CompleteOnboardingResponse,
  OnboardingPayload,
  OnboardingState,
  KIEQuestionsResponse,
  OnboardingAnswersPayload,
  OnboardingAnswersResponse,
} from '@/types/onboarding';

function getAuthHeaders(): HeadersInit {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error('Authentication required. Please log in again.');
  }

  return {
    Authorization: `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  };
}

export function getOnboardingState() {
  return apiRequest<OnboardingState>(
    '/api/v1/onboarding',
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );
}

export function initializeOnboarding(
  payload: OnboardingPayload
) {
  return apiRequest<OnboardingState>(
    '/api/v1/onboarding',
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    }
  );
}

export function updateOnboarding(
  payload: OnboardingPayload
) {
  return apiRequest<OnboardingState>(
    '/api/v1/onboarding',
    {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    }
  );
}

export function completeOnboarding() {
  return apiRequest<CompleteOnboardingResponse>(
    '/api/v1/onboarding/complete',
    {
      method: 'POST',
      headers: getAuthHeaders(),
    }
  );
}

export function getKIEQuestions() {
  return apiRequest<KIEQuestionsResponse>(
    '/api/v1/onboarding/questions',
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );
}

export function submitKIEAnswers(
  payload: OnboardingAnswersPayload
) {
  return apiRequest<OnboardingAnswersResponse>(
    '/api/v1/onboarding/answers',
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    }
  );
}