import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import type {
  ExplicitDirective,
  ExplicitDirectiveCreatePayload,
  StudentProfile,
  StudentProfileCreatePayload,
} from '@/types/profile';

function getAuthHeaders(): HeadersInit {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error('Authentication required. Please log in again.');
  }

  return {
    Authorization: `Bearer ${accessToken}`,
  };
}

export function getProfile() {
  return apiRequest<StudentProfile>('/api/v1/profile', {
    method: 'GET',
    headers: getAuthHeaders(),
  });
}

export function saveProfile(
  payload: StudentProfileCreatePayload
) {
  return apiRequest<StudentProfile>('/api/v1/profile', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
}

export function addExplicitDirective(
  payload: ExplicitDirectiveCreatePayload
) {
  return apiRequest<ExplicitDirective>('/api/v1/profile/directives', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
}

export function deleteExplicitDirective(
  directiveId: string
) {
  return apiRequest<{ message: string }>(
    `/api/v1/profile/directives/${directiveId}`,
    {
      method: 'DELETE',
      headers: getAuthHeaders(),
    }
  );
}