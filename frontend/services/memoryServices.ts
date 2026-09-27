import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import type {
  ApiMessageResponse,
  ContextPayload,
  MemoryLog,
  MemoryLogCreatePayload,
  MemoryResetPayload,
} from '@/types/memory';

function getAuthHeaders(): HeadersInit {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error('Authentication required. Please log in again.');
  }

  return {
    Authorization: `Bearer ${accessToken}`,
  };
}

export function getAIContext() {
  return apiRequest<ContextPayload>('/api/v1/context/retrieve', {
    method: 'GET',
    headers: getAuthHeaders(),
  });
}

export function logMemory(
  payload: MemoryLogCreatePayload
) {
  return apiRequest<MemoryLog>('/api/v1/memory/logs', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
}

export function resetAIMemory(
  payload: MemoryResetPayload
) {
  return apiRequest<ApiMessageResponse>('/api/v1/memory/reset', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
}

export function deleteMemoryLog(
  memoryId: string
) {
  return apiRequest<ApiMessageResponse>(
    `/api/v1/memory/logs/${memoryId}`,
    {
      method: 'DELETE',
      headers: getAuthHeaders(),
    }
  );
}