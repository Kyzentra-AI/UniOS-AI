'use client';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import {
  deleteMemoryLog,
  getAIContext,
  logMemory,
  resetAIMemory,
} from '@/services/memoryServices';

import type {
  MemoryLogCreatePayload,
  MemoryResetPayload,
} from '@/types/memory';

export function useMemory() {
  const queryClient = useQueryClient();

  const contextQuery = useQuery({
    queryKey: ['ai-context'],
    queryFn: getAIContext,
    retry: false,
  });

  const logMemoryMutation = useMutation({
    mutationFn: (payload: MemoryLogCreatePayload) =>
      logMemory(payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['ai-context'],
      });
    },
  });

  const resetMemoryMutation = useMutation({
    mutationFn: (payload: MemoryResetPayload) =>
      resetAIMemory(payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['ai-context'],
      });
    },
  });

  const deleteMemoryMutation = useMutation({
    mutationFn: (memoryId: string) =>
      deleteMemoryLog(memoryId),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['ai-context'],
      });
    },
  });

  return {
    ...contextQuery,

    context: contextQuery.data,

    logMemory: logMemoryMutation.mutateAsync,
    isLoggingMemory: logMemoryMutation.isPending,
    logMemoryError: logMemoryMutation.error,

    resetMemory: resetMemoryMutation.mutateAsync,
    isResettingMemory: resetMemoryMutation.isPending,
    resetMemoryError: resetMemoryMutation.error,

    deleteMemory: deleteMemoryMutation.mutateAsync,
    isDeletingMemory: deleteMemoryMutation.isPending,
    deleteMemoryError: deleteMemoryMutation.error,
  };
}