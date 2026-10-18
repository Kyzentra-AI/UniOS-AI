import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';
import type {
  Artifact, ArtifactVersion, BuildCoachRequest, BuildCoachResponse, CreateArtifactInput,
  CreateArtifactVersionInput, CreateEvidenceInput, CreateMilestoneInput, CreateProjectInput,
  CreateTaskInput, Evidence, Milestone, Project, ProjectRecommendationResponse,
  RecommendedProject, Task, UpdateMilestoneInput, UpdateProjectInput, UpdateTaskInput,
} from '@/types/build';

const BASE = '/api/v1/build';
function getAuthHeaders(): HeadersInit {
  const token = getAccessToken();
  if (!token) throw new Error('Authentication required. Please log in again.');
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}
function jsonBody(value: unknown): string { return JSON.stringify(value); }

export const buildServices = {
  async getRecommendations(): Promise<RecommendedProject[]> {
    const response = await apiRequest<ProjectRecommendationResponse>(`${BASE}/recommendations`, { method: 'GET', headers: getAuthHeaders() });
    return Array.isArray(response?.recommendations) ? response.recommendations : [];
  },
  async listProjects(): Promise<Project[]> {
    const response = await apiRequest<Project[] | { projects?: Project[] }>(`${BASE}/projects`, { method: 'GET', headers: getAuthHeaders() });
    return Array.isArray(response) ? response : response?.projects ?? [];
  },
  createProject(payload: CreateProjectInput): Promise<Project> {
    return apiRequest<Project>(`${BASE}/projects`, { method: 'POST', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  getProject(projectId: string): Promise<Project> {
    return apiRequest<Project>(`${BASE}/projects/${encodeURIComponent(projectId)}`, { method: 'GET', headers: getAuthHeaders() });
  },
  updateProject(projectId: string, payload: UpdateProjectInput): Promise<Project> {
    return apiRequest<Project>(`${BASE}/projects/${encodeURIComponent(projectId)}`, { method: 'PATCH', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  async getMilestones(projectId: string): Promise<Milestone[]> {
    const response = await apiRequest<Milestone[] | { milestones?: Milestone[] }>(`${BASE}/projects/${encodeURIComponent(projectId)}/milestones`, { method: 'GET', headers: getAuthHeaders() });
    return Array.isArray(response) ? response : response?.milestones ?? [];
  },
  async getTasks(projectId: string): Promise<Task[]> {
    const response = await apiRequest<Task[] | { tasks?: Task[] }>(`${BASE}/projects/${encodeURIComponent(projectId)}/tasks`, { method: 'GET', headers: getAuthHeaders() });
    return Array.isArray(response) ? response : response?.tasks ?? [];
  },
  async getArtifacts(projectId: string): Promise<Artifact[]> {
    const response = await apiRequest<Artifact[] | { artifacts?: Artifact[] }>(`${BASE}/projects/${encodeURIComponent(projectId)}/artifacts`, { method: 'GET', headers: getAuthHeaders() });
    return Array.isArray(response) ? response : response?.artifacts ?? [];
  },
  async getEvidence(projectId: string): Promise<Evidence[]> {
    const response = await apiRequest<Evidence[] | { evidence?: Evidence[] }>(`${BASE}/projects/${encodeURIComponent(projectId)}/evidence`, { method: 'GET', headers: getAuthHeaders() });
    return Array.isArray(response) ? response : response?.evidence ?? [];
  },
  generatePlan(projectId: string): Promise<unknown> {
    return apiRequest(`${BASE}/projects/${encodeURIComponent(projectId)}/plan-generate`, { method: 'POST', headers: getAuthHeaders() });
  },
  createMilestone(input: CreateMilestoneInput): Promise<Milestone> {
    const { projectId, ...payload } = input;
    return apiRequest<Milestone>(`${BASE}/projects/${encodeURIComponent(projectId)}/milestones`, { method: 'POST', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  updateMilestone(milestoneId: string, payload: UpdateMilestoneInput): Promise<Milestone> {
    return apiRequest<Milestone>(`${BASE}/milestones/${encodeURIComponent(milestoneId)}`, { method: 'PATCH', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  createTask(input: CreateTaskInput): Promise<Task> {
    const { projectId, ...payload } = input;
    return apiRequest<Task>(`${BASE}/projects/${encodeURIComponent(projectId)}/tasks`, { method: 'POST', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  updateTask(taskId: string, payload: UpdateTaskInput): Promise<Task> {
    return apiRequest<Task>(`${BASE}/tasks/${encodeURIComponent(taskId)}`, { method: 'PATCH', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  createArtifact(input: CreateArtifactInput): Promise<Artifact> {
    const { projectId, ...payload } = input;
    return apiRequest<Artifact>(`${BASE}/projects/${encodeURIComponent(projectId)}/artifacts`, { method: 'POST', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  createArtifactVersion(artifactId: string, payload: CreateArtifactVersionInput): Promise<ArtifactVersion> {
    const body = { file_name: payload.fileName, file_size: payload.fileSize, storage_key: payload.storageKey };
    return apiRequest<ArtifactVersion>(`${BASE}/artifacts/${encodeURIComponent(artifactId)}/versions`, { method: 'POST', headers: getAuthHeaders(), body: jsonBody(body) });
  },
  createEvidence(input: CreateEvidenceInput): Promise<Evidence> {
    const { projectId, ...payload } = input;
    return apiRequest<Evidence>(`${BASE}/projects/${encodeURIComponent(projectId)}/evidence`, { method: 'POST', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  askCoach(projectId: string, payload: BuildCoachRequest): Promise<BuildCoachResponse> {
    return apiRequest<BuildCoachResponse>(`${BASE}/projects/${encodeURIComponent(projectId)}/coach`, { method: 'POST', headers: getAuthHeaders(), body: jsonBody(payload) });
  },
  completeProject(projectId: string): Promise<Project> {
    return apiRequest<Project>(`${BASE}/projects/${encodeURIComponent(projectId)}/complete`, { method: 'POST', headers: getAuthHeaders() });
  },
};
