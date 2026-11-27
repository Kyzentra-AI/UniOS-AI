
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

import {
  deleteSettingsAccount,
  getSettingsAccount,
  getSettingsContext,
  getSettingsFiles,
  getSettingsPreferences,
  getSettingsProfile,
  updateSettingsPreferences,
  updateSettingsProfile,
  uploadSettingsAvatar,
} from '@/services/settingsServices';

import type {
  DeleteAccountPayload,
  FileCategory,
  SettingsPreferencesPatch,
  SettingsProfilePatch,
} from '@/types/settings';

export const settingsKeys = {
  all: ['settings'] as const,
  profile: () => [...settingsKeys.all, 'profile'] as const,
  context: () => [...settingsKeys.all, 'context'] as const,
  files: (category: FileCategory) =>
    [...settingsKeys.all, 'files', category] as const,
  preferences: () => [...settingsKeys.all, 'preferences'] as const,
  account: () => [...settingsKeys.all, 'account'] as const,
};

export function useSettingsProfile() {
  return useQuery({
    queryKey: settingsKeys.profile(),
    queryFn: getSettingsProfile,
    retry: false,
  });
}

export function useSettingsContext() {
  return useQuery({
    queryKey: settingsKeys.context(),
    queryFn: getSettingsContext,
    retry: false,
  });
}

export function useSettingsFiles(category: FileCategory) {
  return useQuery({
    queryKey: settingsKeys.files(category),
    queryFn: () => getSettingsFiles(category),
    retry: false,
  });
}

export function useSettingsPreferences() {
  return useQuery({
    queryKey: settingsKeys.preferences(),
    queryFn: getSettingsPreferences,
    retry: false,
  });
}

export function useSettingsAccount() {
  return useQuery({
    queryKey: settingsKeys.account(),
    queryFn: getSettingsAccount,
    retry: false,
  });
}

export function useUpdateSettingsProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SettingsProfilePatch) =>
      updateSettingsProfile(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: settingsKeys.profile(),
      });
      queryClient.invalidateQueries({
        queryKey: settingsKeys.context(),
      });
    },
  });
}

export function useUploadSettingsAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: uploadSettingsAvatar,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: settingsKeys.profile(),
      });
    },
  });
}

export function useUpdateSettingsPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SettingsPreferencesPatch) =>
      updateSettingsPreferences(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: settingsKeys.preferences(),
      });
      queryClient.invalidateQueries({
        queryKey: settingsKeys.context(),
      });
    },
  });
}

export function useDeleteSettingsAccount() {
  return useMutation({
    mutationFn: (payload: DeleteAccountPayload) =>
      deleteSettingsAccount(payload),
  });
}
