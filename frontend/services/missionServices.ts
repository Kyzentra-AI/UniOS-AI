
import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import {
  completeMissionResponseSchema,
  missionResponseSchema,
} from '@/app/validations/mission';

import type {
  CompleteMissionResponse,
  MissionResponse,
} from '@/types/mission';

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

export async function getMission(
  missionId: string
): Promise<MissionResponse> {
  const response =
    await apiRequest<MissionResponse>(
      `/api/v1/missions/${missionId}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );

  return missionResponseSchema.parse(
    response
  );
}

export async function startMission(
  missionId: string
): Promise<MissionResponse> {
  const response =
    await apiRequest<MissionResponse>(
      `/api/v1/missions/${missionId}/start`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );

  return missionResponseSchema.parse(
    response
  );
}

export async function completeMission(
  missionId: string
): Promise<CompleteMissionResponse> {
  const response =
    await apiRequest<CompleteMissionResponse>(
      `/api/v1/missions/${missionId}/complete`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );

  return completeMissionResponseSchema.parse(
    response
  );
}

export async function deferMission(
  missionId: string
): Promise<MissionResponse> {
  const response =
    await apiRequest<MissionResponse>(
      `/api/v1/missions/${missionId}/defer`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );

  return missionResponseSchema.parse(
    response
  );
}

export async function skipMission(
  missionId: string
): Promise<MissionResponse> {
  const response =
    await apiRequest<MissionResponse>(
      `/api/v1/missions/${missionId}/skip`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );

  return missionResponseSchema.parse(
    response
  );
}