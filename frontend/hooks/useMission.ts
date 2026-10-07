'use client';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import {
  completeMission,
  deferMission,
  getMission,
  skipMission,
  startMission,
} from '@/services/missionServices';

export function useMission(
  missionId?: string
) {
  const queryClient = useQueryClient();

  const missionQuery = useQuery({
    queryKey: ['mission', missionId],
    queryFn: () => getMission(missionId!),
    enabled: Boolean(missionId),
  });

  const invalidateMissionData = () => {
    queryClient.invalidateQueries({
      queryKey: ['mission', missionId],
    });

    queryClient.invalidateQueries({
      queryKey: ['roadmap', 'current'],
    });
  };

  const startMutation = useMutation({
    mutationFn: (id: string) =>
      startMission(id),

    onSuccess: invalidateMissionData,
  });

  const completeMutation = useMutation({
    mutationFn: (id: string) =>
      completeMission(id),

    onSuccess: invalidateMissionData,
  });

  const deferMutation = useMutation({
    mutationFn: (id: string) =>
      deferMission(id),

    onSuccess: invalidateMissionData,
  });

  const skipMutation = useMutation({
    mutationFn: (id: string) =>
      skipMission(id),

    onSuccess: invalidateMissionData,
  });

  return {
    mission: missionQuery.data,

    isLoading: missionQuery.isLoading,
    error: missionQuery.error,

    startMission:
      startMutation.mutateAsync,
    isStarting:
      startMutation.isPending,
    startError:
      startMutation.error,

    completeMission:
      completeMutation.mutateAsync,
    isCompleting:
      completeMutation.isPending,
    completeError:
      completeMutation.error,

    deferMission:
      deferMutation.mutateAsync,
    isDeferring:
      deferMutation.isPending,
    deferError:
      deferMutation.error,

    skipMission:
      skipMutation.mutateAsync,
    isSkipping:
      skipMutation.isPending,
    skipError:
      skipMutation.error,
  };
}
