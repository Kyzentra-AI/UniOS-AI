import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import {
  syllabusMessageResponseSchema,
  syllabusSchema,
  syllabusStatusResponseSchema,
  syllabusUploadResponseSchema,
} from '@/app/validations/syllabus';

import type {
  ParsedSyllabusContent,
  Syllabus,
  SyllabusStatusResponse,
  SyllabusUpdatePayload,
  SyllabusUploadPayload,
  SyllabusUploadResponse,
} from '@/types/syllabus';

function getAuthHeaders(): HeadersInit {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error(
      'Authentication required. Please log in again.'
    );
  }

  return {
    Authorization: `Bearer ${accessToken}`,
  };
}

export async function uploadSyllabus(
  payload: SyllabusUploadPayload
): Promise<SyllabusUploadResponse> {
  const formData = new FormData();

  formData.append('file', payload.file);

  const response = await apiRequest<SyllabusUploadResponse>(
    '/api/v1/syllabi',
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    }
  );

  return syllabusUploadResponseSchema.parse(response);
}

export async function getSyllabusStatus(
  syllabusId: string
): Promise<SyllabusStatusResponse> {
  const response =
    await apiRequest<SyllabusStatusResponse>(
      `/api/v1/syllabi/${syllabusId}/status`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );

  return syllabusStatusResponseSchema.parse(response);
}

export async function getSyllabus(
  syllabusId: string
): Promise<Syllabus> {
  const response = await apiRequest<Syllabus>(
    `/api/v1/syllabi/${syllabusId}`,
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  return syllabusSchema.parse(response);
}

export async function updateParsedContent(
  syllabusId: string,
  payload: SyllabusUpdatePayload
) {
  const response =
    await apiRequest<{ message: string }>(
      `/api/v1/syllabi/${syllabusId}/parsed-content`,
      {
        method: 'PUT',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }
    );

  return syllabusMessageResponseSchema.parse(response);
}

export async function confirmSyllabus(
  syllabusId: string
) {
  const response =
    await apiRequest<{ message: string }>(
      `/api/v1/syllabi/${syllabusId}/confirm`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );

  return syllabusMessageResponseSchema.parse(response);
}

export async function reprocessSyllabus(
  syllabusId: string
) {
  const response =
    await apiRequest<{
      message: string;
      status: string;
    }>(
      `/api/v1/syllabi/${syllabusId}/reprocess`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      }
    );

  return syllabusMessageResponseSchema.parse(response);
}