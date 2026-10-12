
import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import type {
  Artifact,
  ArtifactVersion,
  BuildCoachRequest,
  BuildCoachResponse,
  CreateArtifactInput,
  CreateArtifactVersionInput,
  CreateEvidenceInput,
  CreateMilestoneInput,
  CreateProjectInput,
  CreateTaskInput,
  Evidence,
  Milestone,
  Project,
  RecommendedProject,
  Task,
  UpdateMilestoneInput,
  UpdateProjectInput,
  UpdateTaskInput,
} from '@/types/build';

const BASE = '/api/v1/build';

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

function jsonBody(body: unknown) {
  return {
    headers: getAuthHeaders(),
    body: JSON.stringify(body),
  };
}

export const buildServices = {
  async listProjects(): Promise<Project[]> {
    return apiRequest<Project[]>(`${BASE}/projects`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
  },

  async getProject(id: string): Promise<Project> {
    return apiRequest<Project>(`${BASE}/projects/${id}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });
  },

  async createProject(input: CreateProjectInput): Promise<Project> {
    return apiRequest<Project>(`${BASE}/projects`, {
      method: 'POST',
      ...jsonBody(input),
    });
  },

  async updateProject(
    id: string,
    input: UpdateProjectInput,
  ): Promise<Project> {
    return apiRequest<Project>(`${BASE}/projects/${id}`, {
      method: 'PATCH',
      ...jsonBody(input),
    });
  },

  async getRecommendations(): Promise<RecommendedProject[]> {
    const result = await apiRequest<
      { recommendations: RecommendedProject[] } | RecommendedProject[]
    >(`${BASE}/recommendations`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return Array.isArray(result)
      ? result
      : result.recommendations ?? [];
  },

  async listMilestones(projectId: string): Promise<Milestone[]> {
    return apiRequest<Milestone[]>(
      `${BASE}/projects/${projectId}/milestones`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      },
    );
  },

  async listTasks(projectId: string): Promise<Task[]> {
    return apiRequest<Task[]>(
      `${BASE}/projects/${projectId}/tasks`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      },
    );
  },

  async listArtifacts(projectId: string): Promise<Artifact[]> {
    return apiRequest<Artifact[]>(
      `${BASE}/projects/${projectId}/artifacts`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      },
    );
  },

  async listEvidence(projectId: string): Promise<Evidence[]> {
    return apiRequest<Evidence[]>(
      `${BASE}/projects/${projectId}/evidence`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      },
    );
  },

  async generatePlan(id: string): Promise<unknown> {
    return apiRequest<unknown>(
      `${BASE}/projects/${id}/plan-generate`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
      },
    );
  },

  async createMilestone(
    input: CreateMilestoneInput,
  ): Promise<Milestone> {
    const { projectId, ...body } = input;

    return apiRequest<Milestone>(
      `${BASE}/projects/${projectId}/milestones`,
      {
        method: 'POST',
        ...jsonBody(body),
      },
    );
  },

  async updateMilestone(
    id: string,
    input: UpdateMilestoneInput,
  ): Promise<Milestone> {
    return apiRequest<Milestone>(`${BASE}/milestones/${id}`, {
      method: 'PATCH',
      ...jsonBody(input),
    });
  },

  async createTask(input: CreateTaskInput): Promise<Task> {
    const { projectId, ...body } = input;

    return apiRequest<Task>(
      `${BASE}/projects/${projectId}/tasks`,
      {
        method: 'POST',
        ...jsonBody(body),
      },
    );
  },

  async updateTask(
    id: string,
    input: UpdateTaskInput,
  ): Promise<Task> {
    return apiRequest<Task>(`${BASE}/tasks/${id}`, {
      method: 'PATCH',
      ...jsonBody(input),
    });
  },

  async createArtifact(input: CreateArtifactInput): Promise<Artifact> {
    const { projectId, ...body } = input;

    return apiRequest<Artifact>(
      `${BASE}/projects/${projectId}/artifacts`,
      {
        method: 'POST',
        ...jsonBody(body),
      },
    );
  },

  async createArtifactVersion(
    artifactId: string,
    input: CreateArtifactVersionInput,
  ): Promise<ArtifactVersion> {
    return apiRequest<ArtifactVersion>(
      `${BASE}/artifacts/${artifactId}/versions`,
      {
        method: 'POST',
        ...jsonBody({
          file_name: input.fileName,
          file_size: input.fileSize,
          storage_key: input.storageKey,
        }),
      },
    );
  },

  async createEvidence(input: CreateEvidenceInput): Promise<Evidence> {
    const { projectId, ...body } = input;

    return apiRequest<Evidence>(
      `${BASE}/projects/${projectId}/evidence`,
      {
        method: 'POST',
        ...jsonBody(body),
      },
    );
  },

  async askCoach(
    projectId: string,
    input: BuildCoachRequest,
  ): Promise<BuildCoachResponse> {
    return apiRequest<BuildCoachResponse>(
      `${BASE}/projects/${projectId}/coach`,
      {
        method: 'POST',
        ...jsonBody(input),
      },
    );
  },

  async completeProject(id: string): Promise<Project> {
    return apiRequest<Project>(
      `${BASE}/projects/${id}/complete`,
      {
        method: 'POST',
        ...jsonBody({}),
      },
    );
  },
};