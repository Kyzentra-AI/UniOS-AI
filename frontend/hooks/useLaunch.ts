
'use client';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import { launchServices } from '@/services/launchServices';
import type {
  CreateResumeRequest,
  GenerateResumeRequest,
  UpdateResumeRequest,
} from '@/types/launch';

export const launchKeys = {
  all: ['launch'] as const,
  profilePreview: () => [...launchKeys.all, 'profile-preview'] as const,
  resumes: () => [...launchKeys.all, 'resumes'] as const,
  resume: (id: string) => [...launchKeys.resumes(), id] as const,
  atsHistory: () => [...launchKeys.all, 'ats-history'] as const,
  analysis: (id: string) => [...launchKeys.all, 'analysis', id] as const,
};

export function useProfileResumePreview(enabled = true) {
  return useQuery({
    queryKey: launchKeys.profilePreview(),
    queryFn: launchServices.getProfilePreview,
    enabled,
    retry: false,
  });
}

export function useResumes() {
  return useQuery({
    queryKey: launchKeys.resumes(),
    queryFn: launchServices.listResumes,
    retry: false,
  });
}

export function useResume(resumeId: string) {
  return useQuery({
    queryKey: launchKeys.resume(resumeId),
    queryFn: () => launchServices.getResume(resumeId),
    enabled: Boolean(resumeId),
    retry: false,
  });
}

export function useCreateResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateResumeRequest) =>
      launchServices.createResume(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: launchKeys.resumes(),
      });
    },
  });
}

export function useUpdateResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      resumeId,
      payload,
    }: {
      resumeId: string;
      payload: UpdateResumeRequest;
    }) => launchServices.updateResume(resumeId, payload),
    onSuccess: async (_result, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: launchKeys.resumes(),
        }),
        queryClient.invalidateQueries({
          queryKey: launchKeys.resume(variables.resumeId),
        }),
      ]);
    },
  });
}

export function useGenerateResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: GenerateResumeRequest) =>
      launchServices.generateResume(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: launchKeys.resumes(),
      });
    },
  });
}

export function useAnalyzeResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => launchServices.analyzeResume(file),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: launchKeys.atsHistory(),
      });
    },
  });
}

export function useATSHistory(enabled = true) {
  return useQuery({
    queryKey: launchKeys.atsHistory(),
    queryFn: launchServices.getAnalysisHistory,
    enabled,
    retry: false,
  });
}

export function useATSAnalysis(analysisId: string) {
  return useQuery({
    queryKey: launchKeys.analysis(analysisId),
    queryFn: () => launchServices.getAnalysis(analysisId),
    enabled: Boolean(analysisId),
    retry: false,
  });
}
