import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import type {
  ContentReferenceResponse,
  LearningSession,
  LearningSessionCreate,
  LearningSessionUpdate,
  Lesson,
} from '@/types/learning';

const LEARNING_BASE = '/api/v1/learning';

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

export function createLearningSession(
  payload: LearningSessionCreate,
) {
  return apiRequest<LearningSession>(
    `${LEARNING_BASE}/sessions`,
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    },
  );
}

export function getLearningSession(
  sessionId: string,
) {
  return apiRequest<LearningSession>(
    `${LEARNING_BASE}/sessions/${encodeURIComponent(sessionId)}`,
    {
      method: 'GET',
      headers: getAuthHeaders(),
    },
  );
}

export function saveLearningCheckpoint(
  sessionId: string,
  payload: LearningSessionUpdate,
) {
  return apiRequest<LearningSession>(
    `${LEARNING_BASE}/sessions/${encodeURIComponent(sessionId)}/checkpoint`,
    {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    },
  );
}

export function generateLesson(
  sessionId: string,
  payload: Record<string, unknown>,
) {
  return apiRequest<Lesson>(
    `${LEARNING_BASE}/sessions/${encodeURIComponent(sessionId)}/generate-lesson`,
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    },
  );
}

export function getContentReferences(params: {
  syllabus_id: string;
  topic: string;
  keywords?: string[];
}) {
  const searchParams = new URLSearchParams({
    syllabus_id: params.syllabus_id,
    topic: params.topic,
  });

  params.keywords?.forEach((keyword) => {
    searchParams.append('keywords', keyword);
  });

  return apiRequest<ContentReferenceResponse>(
    `${LEARNING_BASE}/references?${searchParams.toString()}`,
    {
      method: 'GET',
      headers: getAuthHeaders(),
    },
  );
}
