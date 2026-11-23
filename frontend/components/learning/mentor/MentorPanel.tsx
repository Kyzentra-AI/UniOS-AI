
'use client';

import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import type {
  MentorMessage,
  MentorMode,
} from '@/types/mentor';

import { sendMentorMessage } from '@/services/mentorServices';
import type { Lesson, LessonBlock } from '@/types/learning';

interface MentorPanelProps {
  lesson: Lesson;
  roadmapId?: string;
  missionId?: string;
  currentBlockIndex: number;
  subject: string;
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

function getStepContent(block?: LessonBlock): string {
  if (!block) return '';

  const parts = [
    block.content && `Content:\n${block.content}`,
    block.code &&
      `Code (${block.language || 'text'}):\n${block.code}`,
    block.caption && `Caption:\n${block.caption}`,
    block.url && `Resource URL:\n${block.url}`,
    block.options?.length &&
      `Options:\n${block.options
        .map((option, index) => `${index + 1}. ${option}`)
        .join('\n')}`,
  ].filter(Boolean);

  return parts.join('\n\n');
}

export default function MentorPanel({
  lesson,
  roadmapId,
  missionId,
  currentBlockIndex,
  subject,
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
  const currentBlock = lesson.blocks[currentBlockIndex];

  const stepTitle =
    currentBlock?.title || `Section ${currentBlockIndex + 1}`;

  const stepContent = getStepContent(currentBlock);

  // Keep the latest message visible inside the independently scrolling chat.
  useEffect(() => {
    const element = listRef.current;

    if (element) {
      element.scrollTo({
        top: element.scrollHeight,
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
          stepIndex: currentBlockIndex + 1,
          stepTitle,
          stepContent,
          totalSteps: lesson.blocks.length,
          subject,
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
    <section className="flex h-full min-h-0 w-full min-w-0 flex-col">
      <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_28px_rgba(24,52,58,0.04)]">

        {/* Header */}
        <div className="shrink-0 border-b border-[var(--border)] p-4 sm:p-5">
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
        <div className="shrink-0 border-b border-[var(--border)] px-4 py-3 sm:px-5">
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
            className="rise mt-2 text-xs text-[var(--text-secondary)]"
          >
            {currentMode?.description}
          </p>
        </div>

        {/* Current lesson context */}
        <div className="flex shrink-0 items-start gap-3 border-b border-[var(--border)] bg-[var(--surface-alt)] px-4 py-3 sm:px-5">
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
              Section {currentBlockIndex + 1} of {lesson.blocks.length}
              {' · '}
              {stepTitle}
            </p>

            <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
              Mode: {currentMode?.label}
            </p>
          </div>
        </div>

        {/* Independently scrollable conversation */}
        <div
          ref={listRef}
          role="log"
          aria-live="polite"
          aria-label="Conversation with your mentor"
          className="min-h-0 flex-1 space-y-4 overflow-y-auto overscroll-contain p-4 sm:p-5"
        >
          {messages.length === 0 && (
            <div className="flex min-h-full items-center justify-center">
              <div className="max-w-sm text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--surface-alt)] text-lg">
                  ✦
                </div>

                <h3 className="mt-4 text-sm font-semibold text-[var(--text-primary)]">
                  Start a conversation
                </h3>

                <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                  Ask a question about {stepTitle}, request an
                  explanation, or get help planning your next steps.
                </p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`rise flex min-w-0 ${
                message.role === 'user'
                  ? 'justify-end'
                  : 'justify-start'
              }`}
            >
              <div
                className={`min-w-0 max-w-[96%] break-words px-4 py-3 sm:max-w-[92%] ${
                  message.role === 'user'
                    ? 'rounded-2xl rounded-br-md bg-[var(--primary)] text-white'
                    : 'rounded-2xl rounded-bl-md border border-[var(--border)] bg-[var(--surface-alt)] text-[var(--text-primary)]'
                }`}
              >
                {message.role === 'mentor' ? (
                  <div
                    className={[
                      'min-w-0 max-w-full text-sm leading-6',
                      '[&_p]:my-2',
                      '[&_h1]:mb-2 [&_h1]:mt-4 [&_h1]:text-lg [&_h1]:font-bold',
                      '[&_h2]:mb-2 [&_h2]:mt-4 [&_h2]:text-base [&_h2]:font-bold',
                      '[&_h3]:mb-2 [&_h3]:mt-3 [&_h3]:text-sm [&_h3]:font-bold',
                      '[&_strong]:font-semibold',
                      '[&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5',
                      '[&_ol]:my-2 [&_ol]:list-decimal [&_ol]:pl-5',
                      '[&_li]:my-1',
                      '[&_blockquote]:my-3 [&_blockquote]:border-l-2 [&_blockquote]:border-[var(--primary)] [&_blockquote]:pl-3 [&_blockquote]:italic',
                      '[&_a]:break-all [&_a]:text-[var(--feature-blue)] [&_a]:underline',
                      '[&_hr]:my-4 [&_hr]:border-[var(--border)]',
                      '[&_pre]:my-3 [&_pre]:max-w-full [&_pre]:overflow-x-auto [&_pre]:rounded-xl [&_pre]:bg-[var(--surface)] [&_pre]:p-3',
                      '[&_code]:break-words [&_code]:rounded [&_code]:bg-[var(--surface)] [&_code]:px-1 [&_code]:py-0.5 [&_code]:text-xs',
                      '[&_pre_code]:break-normal [&_pre_code]:bg-transparent [&_pre_code]:p-0',
                      '[&_table]:w-full [&_table]:min-w-max [&_table]:border-collapse [&_table]:text-left [&_table]:text-xs',
                      '[&_th]:border [&_th]:border-[var(--border)] [&_th]:bg-[var(--surface)] [&_th]:p-2 [&_th]:font-semibold',
                      '[&_td]:border [&_td]:border-[var(--border)] [&_td]:p-2',
                    ].join(' ')}
                  >
                    <div className="max-w-full overflow-x-auto">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap break-words text-sm leading-6">
                    {message.content}
                  </p>
                )}
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
          <div className="shrink-0 border-t border-[var(--border)] px-4 pt-3 sm:px-5">
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

        {/* Message input stays at the bottom */}
        <div className="shrink-0 border-t border-[var(--border)] bg-[var(--surface)] p-3 sm:p-4">
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
