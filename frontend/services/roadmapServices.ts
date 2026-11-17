
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

export interface CurrentRoadmapParams {
  subject?: string | null;
  scope?: string | null;
}

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

export async function getCurrentRoadmap(
  params: CurrentRoadmapParams = {}
): Promise<RoadmapResponse> {
  const searchParams = new URLSearchParams();

  if (params.subject) {
    searchParams.set('subject', params.subject);
  }

  if (params.scope) {
    searchParams.set('scope', params.scope);
  }

  const queryString = searchParams.toString();

  const endpoint = queryString
    ? `/api/v1/roadmaps/current?${queryString}`
    : '/api/v1/roadmaps/current';

  const response =
    await apiRequest<RoadmapResponse>(
      endpoint,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );

  return roadmapResponseSchema.parse(response);
}
