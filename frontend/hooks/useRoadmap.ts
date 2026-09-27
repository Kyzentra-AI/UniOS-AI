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

import type { RoadmapRequest } from '@/types/roadmap';

export function useRoadmap() {
  const queryClient = useQueryClient();

  const roadmapQuery = useQuery({
    queryKey: ['roadmap', 'current'],
    queryFn: getCurrentRoadmap,

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