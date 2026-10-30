
'use client';

import { useEffect, useRef, useState } from 'react';

import type { Lesson } from '@/types/learning';
import type {
  MentorMessage,
  MentorMode,
} from '@/types/mentor';

import { sendMentorMessage } from '@/services/mentorServices';

interface MentorPanelProps {
  lesson: Lesson;
  roadmapId?: string;
  missionId?: string;
}

const modes: {
  id: MentorMode;
  label: string;
  description: string;
}[] = [
  {
    id: 'tutor',
    label: 'Tutor',
    description: 'Understand the current concept.',
  },
  {
    id: 'study-coach',
    label: 'Study Coach',
    description: 'Plan and structure your learning.',
  },
  {
    id: 'accountability',
    label: 'Accountability',
    description: 'Stay on track with your mission.',
  },
  {
    id: 'motivation',
    label: 'Motivation',
    description: 'Get encouragement when you need it.',
  },
];

export default function MentorPanel({
  lesson,
  roadmapId,
  missionId,
}: MentorPanelProps) {
  const [mode, setMode] = useState<MentorMode>('tutor');
  const [messages, setMessages] = useState<MentorMessage[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(
    null,
  );

  const listRef = useRef<HTMLDivElement>(null);

  const currentMode = modes.find((item) => item.id === mode);

  useEffect(() => {
    const el = listRef.current;

    if (el) {
      el.scrollTo({
        top: el.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages, isTyping]);

  async function handleSend() {
    const trimmedInput = input.trim();

    if (!trimmedInput || isTyping) {
      return;
    }

    const userMessage: MentorMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmedInput,
      createdAt: new Date().toISOString(),
    };

    // Snapshot history before adding the current message.
    const history = messages.map(({ role, content }) => ({
      role,
      content,
    }));

    setMessages((current) => [...current, userMessage]);
    setInput('');
    setIsTyping(true);
    setError(null);

    try {
      const response = await sendMentorMessage({
        mode,
        message: trimmedInput,
        context: {
          lessonId: lesson.id,
          topic: lesson.title,
          roadmapId,
          missionId,
        },
        history,
        conversationId,
      });

      setConversationId(response.conversationId);

      const mentorMessage: MentorMessage = {
        id: `mentor-${Date.now()}`,
        role: 'mentor',
        content: response.reply,
        createdAt: response.createdAt ?? new Date().toISOString(),
      };

      setMessages((current) => [...current, mentorMessage]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to connect to the mentor. Please try again.',
      );
    } finally {
      setIsTyping(false);
    }
  }

  return (
    <section className="w-full min-w-0">
      <div className="overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_28px_rgba(24,52,58,0.04)]">
        {/* Header */}
        <div className="border-b border-[var(--border)] p-4 sm:p-5">
          <p className="text-sm font-medium text-[var(--feature-blue)]">
            AI Mentor
          </p>

          <h2 className="mt-1 text-xl font-semibold text-[var(--text-primary)]">
            Learn with context
          </h2>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            Ask questions about your current lesson and get guidance
            tailored to your selected mentor mode.
          </p>
        </div>

        {/* Mentor modes */}
        <div className="border-b border-[var(--border)] px-4 py-4 sm:px-5">
          <div
            role="radiogroup"
            aria-label="Mentor mode"
            className="flex flex-wrap gap-2"
          >
            {modes.map((item) => {
              const active = mode === item.id;

              return (
                <button
                  key={item.id}
                  type="button"
                  role="radio"
                  aria-checked={active}
                  onClick={() => setMode(item.id)}
                  className={`shrink-0 rounded-full border px-3 py-2 text-xs font-medium transition active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] ${
                    active
                      ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                      : 'border-[var(--border)] text-[var(--text-secondary)] hover:border-[var(--primary)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  {item.label}
                </button>
              );
            })}
          </div>

          <p
            key={mode}
            className="rise mt-3 text-sm text-[var(--text-secondary)]"
          >
            {currentMode?.description}
          </p>
        </div>

        {/* Current lesson context */}
        <div className="flex items-start gap-3 border-b border-[var(--border)] bg-[var(--surface-alt)] px-4 py-3 sm:px-5">
          <span
            aria-hidden="true"
            className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[var(--feature-blue)]"
          />

          <div className="min-w-0">
            <p className="text-xs text-[var(--text-muted)]">
              Current context
            </p>

            <p className="mt-0.5 truncate text-sm font-medium text-[var(--text-primary)]">
              {lesson.title}
            </p>

            <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
              Mode: {currentMode?.label}
            </p>
          </div>
        </div>

        {/* Conversation */}
        <div
          ref={listRef}
          role="log"
          aria-live="polite"
          aria-label="Conversation with your mentor"
          className="h-[min(60vh,440px)] min-h-[300px] space-y-4 overflow-y-auto p-4 sm:p-5"
        >
          {messages.length === 0 && (
            <div className="flex min-h-[240px] items-center justify-center">
              <div className="max-w-sm text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--surface-alt)] text-lg">
                  ✦
                </div>

                <h3 className="mt-4 text-sm font-semibold text-[var(--text-primary)]">
                  Start a conversation
                </h3>

                <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                  Ask a question about {lesson.title}, request an
                  explanation, or get help planning your next steps.
                </p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`rise flex ${
                message.role === 'user'
                  ? 'justify-end'
                  : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[92%] px-4 py-3 sm:max-w-[88%] ${
                  message.role === 'user'
                    ? 'rounded-2xl rounded-br-md bg-[var(--primary)] text-white'
                    : 'rounded-2xl rounded-bl-md border border-[var(--border)] bg-[var(--surface-alt)] text-[var(--text-primary)]'
                }`}
              >
                <p className="whitespace-pre-wrap break-words text-sm leading-6">
                  {message.content}
                </p>
              </div>
            </div>
          ))}

          {isTyping && (
            <div
              className="rise flex justify-start"
              role="status"
              aria-label="Mentor is responding"
            >
              <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md border border-[var(--border)] bg-[var(--surface-alt)] px-4 py-3.5">
                {[0, 1, 2].map((n) => (
                  <span
                    key={n}
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--text-muted)]"
                    style={{ animationDelay: `${n * 0.15}s` }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* API error */}
        {error && (
          <div className="border-t border-[var(--border)] px-4 pt-4 sm:px-5">
            <div
              role="alert"
              className="flex items-start justify-between gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              <p className="leading-6">{error}</p>

              <button
                type="button"
                onClick={() => setError(null)}
                aria-label="Dismiss error"
                className="shrink-0 font-semibold"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Message input */}
        <div className="border-t border-[var(--border)] p-3 sm:p-4">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              void handleSend();
            }}
          >
            <div className="flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)] py-1.5 pl-4 pr-1.5 transition focus-within:border-[var(--primary)] focus-within:shadow-[0_0_0_4px_var(--primary-soft)]">
              <input
                type="text"
                value={input}
                aria-label="Message your mentor"
                onChange={(event) => setInput(event.target.value)}
                placeholder={`Ask your ${currentMode?.label.toLowerCase()}...`}
                disabled={isTyping}
                className="min-w-0 flex-1 bg-transparent py-2 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] disabled:opacity-60"
              />

              <button
                type="submit"
                disabled={!input.trim() || isTyping}
                className="shrink-0 rounded-full bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
              >
                {isTyping ? 'Sending…' : 'Send'}
              </button>
            </div>
          </form>

          <p className="mt-2.5 pl-2 text-xs text-[var(--text-muted)]">
            Responses are generated through your connected mentor API.
          </p>
        </div>
      </div>
    </section>
  );
}
