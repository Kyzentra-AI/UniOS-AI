
import { apiRequest } from '@/lib/api';
import type {
  ATSAnalysisHistoryResponse,
  ATSAnalysisResponse,
  CreateResumeRequest,
  GenerateResumeRequest,
  GenerateResumeResponse,
  ProfileResumePreviewResponse,
  ResumeDetailResponse,
  ResumeListResponse,
  UpdateResumeRequest,
} from '@/types/launch';

// Proposed routes: confirm these with the backend before integration.
const BASE = '/api/v1/launch';

export const launchServices = {
  getProfilePreview: () =>
    apiRequest<ProfileResumePreviewResponse>(
      `${BASE}/resumes/profile-preview`,
    ),

  listResumes: () =>
    apiRequest<ResumeListResponse>(`${BASE}/resumes`),

  getResume: (resumeId: string) =>
    apiRequest<ResumeDetailResponse>(
      `${BASE}/resumes/${encodeURIComponent(resumeId)}`,
    ),

  createResume: (payload: CreateResumeRequest) =>
    apiRequest<ResumeDetailResponse>(`${BASE}/resumes`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateResume: (
    resumeId: string,
    payload: UpdateResumeRequest,
  ) =>
    apiRequest<ResumeDetailResponse>(
      `${BASE}/resumes/${encodeURIComponent(resumeId)}`,
      {
        method: 'PATCH',
        body: JSON.stringify(payload),
      },
    ),

  generateResume: (payload: GenerateResumeRequest) =>
    apiRequest<GenerateResumeResponse>(`${BASE}/resumes/generate`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  analyzeResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    return apiRequest<ATSAnalysisResponse>(
      `${BASE}/ats/analyses`,
      {
        method: 'POST',
        body: formData,
      },
    );
  },

  getAnalysis: (analysisId: string) =>
    apiRequest<ATSAnalysisResponse>(
      `${BASE}/ats/analyses/${encodeURIComponent(analysisId)}`,
    ),

  getAnalysisHistory: () =>
    apiRequest<ATSAnalysisHistoryResponse>(
      `${BASE}/ats/analyses`,
    ),
};
