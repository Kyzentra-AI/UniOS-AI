'use client';

import { useState } from 'react';

import type {
  MentorMessage,
  MentorMode,
} from '@/types/mentor';

interface UseMentorOptions {
  initialMode?: MentorMode;
}

export function useMentor({
  initialMode = 'tutor',
}: UseMentorOptions = {}) {
  const [mode, setMode] =
    useState<MentorMode>(initialMode);

  const [messages, setMessages] = useState<MentorMessage[]>(
    []
  );

  const [input, setInput] = useState('');

  const [isSending, setIsSending] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const addMessage = (message: MentorMessage) => {
    setMessages((current) => [...current, message]);
  };

  const clearMessages = () => {
    setMessages([]);
  };

  const resetMentor = () => {
    setMode(initialMode);
    setMessages([]);
    setInput('');
    setIsSending(false);
    setError(null);
  };

  return {
    mode,
    setMode,

    messages,
    addMessage,
    clearMessages,

    input,
    setInput,

    isSending,
    setIsSending,

    error,
    setError,

    resetMentor,
  };
}