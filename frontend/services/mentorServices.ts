import { apiRequest } from '@/lib/api';
import { getAccessToken } from '@/lib/auth';

import type {
  MentorContext,
  MentorMessage,
  MentorMode,
} from '@/types/mentor';

export interface SendMentorMessagePayload {
  mode: MentorMode;
  message: string;
  context: MentorContext;
  history: Pick<MentorMessage, 'role' | 'content'>[];
  conversationId?: string | null;
}

export interface MentorChatResponse {
  reply: string;
  conversationId: string;
  createdAt?: string;
}

export async function sendMentorMessage(
  payload: SendMentorMessagePayload,
): Promise<MentorChatResponse> {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error('Authentication required. Please log in again.');
  }

  return apiRequest<MentorChatResponse>(
    '/api/v1/mentor/chat',
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    },
  );
}