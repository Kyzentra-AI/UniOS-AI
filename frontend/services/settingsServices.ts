
import { apiRequest } from '@/lib/api';

import type {
  DeleteAccountPayload,
  DownloadableFileCategory,
  FileCategory,
  SettingsAccount,
  SettingsAIContext,
  SettingsAvatarResponse,
  SettingsFileDownloadResponse,
  SettingsFilesResponse,
  SettingsPreferences,
  SettingsPreferencesPatch,
  SettingsProfile,
  SettingsProfilePatch,
  SettingsMessageResponse,
} from '@/types/settings';

const BASE_URL = '/api/v1/settings';

export const getSettingsProfile = () =>
  apiRequest<SettingsProfile>(`${BASE_URL}/profile`);

export const updateSettingsProfile = (
  payload: SettingsProfilePatch
) =>
  apiRequest<SettingsProfile>(`${BASE_URL}/profile`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });

export const uploadSettingsAvatar = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  return apiRequest<SettingsAvatarResponse>(
    `${BASE_URL}/profile/avatar`,
    {
      method: 'POST',
      body: formData,
    }
  );
};

export const getSettingsContext = () =>
  apiRequest<SettingsAIContext>(`${BASE_URL}/context`);

export const getSettingsFiles = (category: FileCategory = 'ALL') =>
  apiRequest<SettingsFilesResponse>(
    `${BASE_URL}/files?category=${encodeURIComponent(category)}`
  );

export const getSettingsFileDownload = (
  category: DownloadableFileCategory,
  fileId: string
) =>
  apiRequest<SettingsFileDownloadResponse>(
    `${BASE_URL}/files/${category}/${encodeURIComponent(fileId)}/download`
  );

export const getSettingsPreferences = () =>
  apiRequest<SettingsPreferences>(`${BASE_URL}/preferences`);

export const updateSettingsPreferences = (
  payload: SettingsPreferencesPatch
) =>
  apiRequest<SettingsPreferences>(`${BASE_URL}/preferences`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });

export const getSettingsAccount = () =>
  apiRequest<SettingsAccount>(`${BASE_URL}/account`);

export const deleteSettingsAccount = (
  payload: DeleteAccountPayload
) =>
  apiRequest<SettingsMessageResponse>(`${BASE_URL}/account/delete`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
