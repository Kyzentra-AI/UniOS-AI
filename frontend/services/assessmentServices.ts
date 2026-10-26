import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import type {
  Assessment,
  AssessmentAttemptCreate,
  AssessmentAttemptResponse,
} from '@/types/assessment';

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

export interface GenerateAssessmentPayload {
  session_id: string;
  topic: string;
}

export async function generateAssessment(
  payload: GenerateAssessmentPayload,
): Promise<Assessment> {
  return apiRequest<Assessment>(
    '/api/v1/assessments/generate',
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    },
  );
}

export function submitAssessmentAttempt(
  payload: AssessmentAttemptCreate,
): Promise<AssessmentAttemptResponse> {
  return apiRequest<AssessmentAttemptResponse>(
    '/api/v1/assessments/attempts',
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    },
  );
}