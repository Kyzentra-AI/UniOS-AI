
'use client';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import {
  generateRoadmap,
  getCurrentRoadmap,
} from '@/services/roadmapServices';

import type {
  CurrentRoadmapParams,
} from '@/services/roadmapServices';

import type { RoadmapRequest } from '@/types/roadmap';

export function useRoadmap(
  params: CurrentRoadmapParams = {}
) {
  const queryClient = useQueryClient();

  const subject = params.subject || null;
  const scope = params.scope || null;

  const roadmapQuery = useQuery({
    queryKey: [
      'roadmap',
      'current',
      subject ?? 'ALL',
      scope ?? 'ALL',
    ],

    queryFn: () =>
      getCurrentRoadmap({
        subject,
        scope,
      }),

    // Preserve the existing generation polling behavior.
    refetchInterval: (query) => {
      const roadmap = query.state.data?.roadmap;

      if (roadmap) {
        return false;
      }

      return 3000;
    },
  });

  const generateMutation = useMutation({
    mutationFn: (payload: RoadmapRequest) =>
      generateRoadmap(payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['roadmap', 'current'],
      });
    },
  });

  return {
    roadmap: roadmapQuery.data?.roadmap ?? null,

    availableSubjects:
      roadmapQuery.data?.available_subjects ?? [],

    activeSubject:
      roadmapQuery.data?.active_subject ?? 'ALL',

    isLoading: roadmapQuery.isLoading,
    isFetching: roadmapQuery.isFetching,
    isError: roadmapQuery.isError,
    error: roadmapQuery.error,

    refetch: roadmapQuery.refetch,

    generateRoadmap:
      generateMutation.mutateAsync,

    isGenerating:
      generateMutation.isPending,

    generateError:
      generateMutation.error,
  };
}
