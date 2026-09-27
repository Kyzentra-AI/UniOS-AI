import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import {
  roadmapGenerationResponseSchema,
  roadmapResponseSchema,
} from '@/app/validations/roadmap';

import type {
  RoadmapGenerationResponse,
  RoadmapRequest,
  RoadmapResponse,
} from '@/types/roadmap';

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

export async function generateRoadmap(
  payload: RoadmapRequest
): Promise<RoadmapGenerationResponse> {
  const response =
    await apiRequest<RoadmapGenerationResponse>(
      '/api/v1/roadmaps',
      {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload),
      }
    );

  return roadmapGenerationResponseSchema.parse(
    response
  );
}

export async function getCurrentRoadmap(): Promise<RoadmapResponse> {
  const response =
    await apiRequest<RoadmapResponse>(
      '/api/v1/roadmaps/current',
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );

  return roadmapResponseSchema.parse(response);
}