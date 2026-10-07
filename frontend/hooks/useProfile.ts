'use client';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import {
  getProfile,
  saveProfile,
} from '@/services/profileServices';



import type {
  StudentProfileCreatePayload,
} from '@/types/profile';

export function useProfile() {
  const queryClient = useQueryClient();

  const profileQuery = useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
    retry: false,
  });

  const saveProfileMutation = useMutation({
    mutationFn: (payload: StudentProfileCreatePayload) =>
      saveProfile(payload),

    onSuccess: (data) => {
      queryClient.setQueryData(['profile'], data);

      queryClient.invalidateQueries({
        queryKey: ['ai-context'],
      });
    },
  });

  return {
    ...profileQuery,

    profile: profileQuery.data,

    saveProfile: saveProfileMutation.mutateAsync,

    isSaving: saveProfileMutation.isPending,
    saveError: saveProfileMutation.error,
  };
}