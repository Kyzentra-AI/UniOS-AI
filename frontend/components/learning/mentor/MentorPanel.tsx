'use client';

import { useEffect, useRef, useState } from 'react';

import type { Lesson } from '@/types/learning';
import type { MentorMessage, MentorMode } from '@/types/mentor';

interface MentorPanelProps {
  lesson: Lesson;
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

const mockMessages: MentorMessage[] = [
  {
    id: 'mentor-message-1',
    role: 'mentor',
    content:
      'You are currently learning DBMS fundamentals. I can help you understand the concept step by step.',
    createdAt: new Date().toISOString(),
  },
  {
    id: 'mentor-message-2',
    role: 'user',
    content: 'Can you explain DBMS in simple words?',
    createdAt: new Date().toISOString(),
  },
  {
    id: 'mentor-message-3',
    role: 'mentor',
    content:
      'Sure. A DBMS is software that helps us store, organize, retrieve, and manage data in a database.',
    createdAt: new Date().toISOString(),
  },
];

export default function MentorPanel({
  lesson,
}: MentorPanelProps) {
  const [mode, setMode] =
    useState<MentorMode>('tutor');

  const [messages, setMessages] =
    useState<MentorMessage[]>(mockMessages);

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  const currentMode = modes.find(
    (item) => item.id === mode
  );

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = () => {
    const trimmedInput = input.trim();

    if (!trimmedInput) {
      return;
    }

    const userMessage: MentorMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmedInput,
      createdAt: new Date().toISOString(),
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setInput('');
    setIsTyping(true);

    // Temporary mock response.
    setTimeout(() => {
      const mentorMessage: MentorMessage = {
        id: `mentor-${Date.now()}`,
        role: 'mentor',
        content:
          'This is a mock mentor response. The actual mentor API will be connected later.',
        createdAt: new Date().toISOString(),
      };

      setMessages((current) => [
        ...current,
        mentorMessage,
      ]);
      setIsTyping(false);
    }, 500);
  };

  return (
    <section className="mx-auto w-full max-w-5xl">
      <div className="overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_28px_rgba(24,52,58,0.04)]">
        {/* Header */}
        <div className="border-b border-[var(--border)] p-5 sm:p-6">
          <p className="text-sm font-medium text-[var(--feature-blue)]">
            Mentor
          </p>

          <h2 className="mt-1 text-xl font-semibold text-[var(--text-primary)]">
            Learn with context
          </h2>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            Mentor is aware of your current lesson and learning
            context.
          </p>
        </div>

        {/* Modes */}
        <div className="border-b border-[var(--border)] px-5 py-4 sm:px-6">
          <div
            role="radiogroup"
            aria-label="Mentor mode"
            className="flex gap-2 overflow-x-auto pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
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
                  className={`shrink-0 whitespace-nowrap rounded-full border px-4 py-2 text-sm font-medium transition active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] ${
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

          <p key={mode} className="rise mt-3 text-sm text-[var(--text-secondary)]">
            {currentMode?.description}
          </p>
        </div>

        {/* Current Context */}
        <div className="flex items-start gap-3 border-b border-[var(--border)] bg-[var(--surface-alt)] px-5 py-3 sm:px-6">
          <span aria-hidden="true" className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[var(--feature-blue)]" />
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

        {/* Messages */}
        <div
          ref={listRef}
          role="log"
          aria-live="polite"
          aria-label="Conversation with your mentor"
          className="h-[min(60vh,440px)] min-h-[300px] space-y-4 overflow-y-auto p-5 sm:p-6"
        >
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
                className={`max-w-[88%] px-4 py-3 sm:max-w-[75%] ${
                  message.role === 'user'
                    ? 'rounded-2xl rounded-br-md bg-[var(--primary)] text-white'
                    : 'rounded-2xl rounded-bl-md border border-[var(--border)] bg-[var(--surface-alt)] text-[var(--text-primary)]'
                }`}
              >
                <p className="break-words text-sm leading-6">
                  {message.content}
                </p>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="rise flex justify-start" aria-label="Mentor is typing">
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

        {/* Input */}
        <div className="border-t border-[var(--border)] p-4 sm:p-5">
          <div className="flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)] py-1.5 pl-5 pr-1.5 transition focus-within:border-[var(--primary)] focus-within:shadow-[0_0_0_4px_var(--primary-soft)]">
            <input
              type="text"
              value={input}
              aria-label="Message your mentor"
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  handleSend();
                }
              }}
              placeholder={`Ask your ${currentMode?.label.toLowerCase()}...`}
              className="min-w-0 flex-1 bg-transparent py-2 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)]"
            />

            <button
              type="button"
              onClick={handleSend}
              disabled={!input.trim()}
              className="shrink-0 rounded-full bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] active:scale-[0.97] disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
            >
              Send
            </button>
          </div>

          <p className="mt-2.5 pl-2 text-xs text-[var(--text-muted)]">
            Mock mentor interaction — backend connection will be added later.
          </p>
        </div>
      </div>
    </section>
  );
}