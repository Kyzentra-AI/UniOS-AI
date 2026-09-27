'use client';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import {
  confirmSyllabus,
  getSyllabus,
  getSyllabusStatus,
  reprocessSyllabus,
  updateParsedContent,
  uploadSyllabus,
} from '@/services/syllabusServices';

export function useSyllabus(
  syllabusId?: string
) {
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: uploadSyllabus,
  });

  const statusQuery = useQuery({
    queryKey: ['syllabus', syllabusId, 'status'],
    queryFn: () => getSyllabusStatus(syllabusId!),
    enabled: Boolean(syllabusId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;

      if (
        status === 'WAITING_FOR_CONFIRMATION' ||
        status === 'CONFIRMED' ||
        status === 'FAILED'
      ) {
        return false;
      }

      return 2000;
    },
  });

  const syllabusQuery = useQuery({
    queryKey: ['syllabus', syllabusId],
    queryFn: () => getSyllabus(syllabusId!),
    enabled: Boolean(syllabusId),
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      parsedContent,
    }: {
      id: string;
      parsedContent: Parameters<
        typeof updateParsedContent
      >[1]['parsed_content'];
    }) =>
      updateParsedContent(id, {
        parsed_content: parsedContent,
      }),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['syllabus', syllabusId],
      });
    },
  });

  const confirmMutation = useMutation({
    mutationFn: confirmSyllabus,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['syllabus', syllabusId],
      });

      queryClient.invalidateQueries({
        queryKey: ['syllabus', syllabusId, 'status'],
      });
    },
  });

  const reprocessMutation = useMutation({
    mutationFn: reprocessSyllabus,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['syllabus', syllabusId],
      });

      queryClient.invalidateQueries({
        queryKey: ['syllabus', syllabusId, 'status'],
      });
    },
  });

  return {
    uploadSyllabus: uploadMutation.mutateAsync,
    isUploading: uploadMutation.isPending,
    uploadError: uploadMutation.error,

    syllabus: syllabusQuery.data,
    isLoadingSyllabus: syllabusQuery.isLoading,
    syllabusError: syllabusQuery.error,

    status: statusQuery.data?.status,
    isLoadingStatus: statusQuery.isLoading,
    statusError: statusQuery.error,

    updateParsedContent:
      updateMutation.mutateAsync,
    isUpdatingParsedContent:
      updateMutation.isPending,
    updateParsedContentError:
      updateMutation.error,

    confirmSyllabus:
      confirmMutation.mutateAsync,
    isConfirming:
      confirmMutation.isPending,
    confirmError:
      confirmMutation.error,

    reprocessSyllabus:
      reprocessMutation.mutateAsync,
    isReprocessing:
      reprocessMutation.isPending,
    reprocessError:
      reprocessMutation.error,
  };
}