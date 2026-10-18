
import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import type {
  AssessmentAttemptCreate,
  AssessmentAttemptResponse,
} from '@/types/assessment';

function getAuthHeaders(): HeadersInit {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error(
      'Authentication required. Please log in again.',
    );
  }

  return {
    Authorization: `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  };
}

export function submitAssessmentAttempt(
  payload: AssessmentAttemptCreate,
) {
  return apiRequest<AssessmentAttemptResponse>(
    '/api/v1/assessments/attempts',
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    },
  );
}
