'use client';

import { useState } from 'react';

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

  const currentMode = modes.find(
    (item) => item.id === mode
  );

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
    }, 500);
  };

  return (
    <section className="mx-auto w-full max-w-5xl">
      <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface)]">
        {/* Header */}
        <div className="border-b border-[var(--border)] p-6">
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
        <div className="border-b border-[var(--border)] p-4">
          <div className="grid gap-2 sm:grid-cols-4">
            {modes.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setMode(item.id)}
                className={`rounded-lg border p-3 text-left transition ${
                  mode === item.id
                    ? 'border-[var(--primary)] bg-[var(--primary-soft)]'
                    : 'border-[var(--border)] hover:bg-[var(--surface-alt)]'
                }`}
              >
                <p className="text-sm font-medium text-[var(--text-primary)]">
                  {item.label}
                </p>

                <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                  {item.description}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Current Context */}
        <div className="border-b border-[var(--border)] bg-[var(--surface-alt)] px-6 py-3">
          <p className="text-xs text-[var(--text-muted)]">
            Current context
          </p>

          <p className="mt-1 text-sm font-medium text-[var(--text-primary)]">
            {lesson.title}
          </p>

          <p className="mt-1 text-xs text-[var(--text-secondary)]">
            Mode: {currentMode?.label}
          </p>
        </div>

        {/* Messages */}
        <div className="min-h-[380px] space-y-4 p-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === 'user'
                  ? 'justify-end'
                  : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[75%] rounded-xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-[var(--primary)] text-white'
                    : 'border border-[var(--border)] bg-[var(--surface-alt)] text-[var(--text-primary)]'
                }`}
              >
                <p className="text-sm leading-6">
                  {message.content}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="border-t border-[var(--border)] p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  handleSend();
                }
              }}
              placeholder={`Ask your ${currentMode?.label.toLowerCase()}...`}
              className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)]"
            />

            <button
              type="button"
              onClick={handleSend}
              className="rounded-lg bg-[var(--primary)] px-5 py-3 text-sm font-medium text-white transition hover:bg-[var(--primary-hover)]"
            >
              Send
            </button>
          </div>

          <p className="mt-2 text-xs text-[var(--text-muted)]">
            Mock mentor interaction — backend connection will be added later.
          </p>
        </div>
      </div>
    </section>
  );
}