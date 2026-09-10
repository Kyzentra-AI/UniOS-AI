
'use client';

import React, { useState } from 'react';
import {
  Brain,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  Edit3,
  Lightbulb,
  Plus,
  RotateCcw,
  Trash2,
  X,
} from 'lucide-react';

type Memory = {
  id: number;
  title: string;
  description: string;
  frequency: number;
  lastObserved: string;
  type: 'friction' | 'memory';
};

type Directive = {
  id: number;
  text: string;
};

const initialFrictionPoints: Memory[] = [
  {
    id: 1,
    title: 'SQL Joins',
    description: 'Needs repeated practice with JOIN conditions and query structure.',
    frequency: 4,
    lastObserved: 'Sep 8, 2026',
    type: 'friction',
  },
  {
    id: 2,
    title: 'Computer Networks',
    description: 'Sometimes confuses TCP and UDP concepts during revision.',
    frequency: 3,
    lastObserved: 'Sep 7, 2026',
    type: 'friction',
  },
  {
    id: 3,
    title: 'Operating Systems',
    description: 'Needs more reinforcement around process scheduling concepts.',
    frequency: 2,
    lastObserved: 'Sep 5, 2026',
    type: 'friction',
  },
];

const initialMemories: Memory[] = [
  {
    id: 4,
    title: 'TCP / UDP confusion',
    description: 'Similar confusion was observed across multiple learning sessions.',
    frequency: 3,
    lastObserved: 'Sep 8, 2026',
    type: 'memory',
  },
  {
    id: 5,
    title: 'Prefers practical examples',
    description: 'Frequently engages better when concepts are connected to real applications.',
    frequency: 5,
    lastObserved: 'Sep 6, 2026',
    type: 'memory',
  },
];

const initialDirectives: Directive[] = [
  {
    id: 1,
    text: 'Explain difficult concepts with practical examples.',
  },
  {
    id: 2,
    text: 'Keep explanations concise and exam-focused when I am preparing for exams.',
  },
];

export default function AIMemoryDashboard() {
  const [frictionPoints, setFrictionPoints] = useState(initialFrictionPoints);
  const [memories, setMemories] = useState(initialMemories);
  const [directives, setDirectives] = useState(initialDirectives);

  const [isAddingDirective, setIsAddingDirective] = useState(false);
  const [newDirective, setNewDirective] = useState('');

  const [editingDirectiveId, setEditingDirectiveId] = useState<number | null>(
    null
  );
  const [editingText, setEditingText] = useState('');

  const [showResetModal, setShowResetModal] = useState(false);

  const deleteMemory = (id: number) => {
    setMemories((current) => current.filter((memory) => memory.id !== id));
    setFrictionPoints((current) =>
      current.filter((memory) => memory.id !== id)
    );
  };

  const addDirective = () => {
    const trimmed = newDirective.trim();

    if (!trimmed) return;

    setDirectives((current) => [
      ...current,
      {
        id: Date.now(),
        text: trimmed,
      },
    ]);

    setNewDirective('');
    setIsAddingDirective(false);
  };

  const startEditingDirective = (directive: Directive) => {
    setEditingDirectiveId(directive.id);
    setEditingText(directive.text);
  };

  const saveDirective = () => {
    const trimmed = editingText.trim();

    if (!trimmed || editingDirectiveId === null) return;

    setDirectives((current) =>
      current.map((directive) =>
        directive.id === editingDirectiveId
          ? { ...directive, text: trimmed }
          : directive
      )
    );

    setEditingDirectiveId(null);
    setEditingText('');
  };

  const deleteDirective = (id: number) => {
    setDirectives((current) =>
      current.filter((directive) => directive.id !== id)
    );
  };

  const resetAIContext = () => {
    setFrictionPoints([]);
    setMemories([]);
    setShowResetModal(false);
  };

  return (
    <main className="min-h-screen bg-[var(--background)] px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--primary-soft)] text-[var(--primary)]">
              <Brain size={22} />
            </div>

            <div>
              <h1 className="text-2xl font-semibold text-[var(--text-primary)]">
                AI Memory
              </h1>
              <p className="text-sm text-[var(--text-secondary)]">
                See what UniOS AI has learned about you.
              </p>
            </div>
          </div>

          <p className="max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">
            Your profile, preferences, learning patterns and explicit
            instructions help UniOS personalise your experience. You stay in
            control of what is remembered.
          </p>
        </div>

        {/* Profile Context */}
        <section className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm sm:p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                Profile Context
              </h2>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                Information currently used to personalise your AI experience.
              </p>
            </div>

            <button
              type="button"
              className="hidden items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-2 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)] sm:flex"
            >
              <Edit3 size={15} />
              Edit Profile
            </button>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <ContextCard
              label="Education"
              value="B.Tech CSE"
              detail="Central University of Punjab"
            />

            <ContextCard
              label="Semester"
              value="5th Semester"
              detail="Undergraduate"
            />

            <ContextCard
              label="Career Goal"
              value="AI / Full Stack"
              detail="Technology"
            />

            <ContextCard
              label="Language"
              value="English"
              detail="Text + Visual learning"
            />
          </div>

          <button
            type="button"
            className="mt-4 flex w-full items-center justify-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-2 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)] sm:hidden"
          >
            <Edit3 size={15} />
            Edit Profile
          </button>
        </section>

        {/* Strengths */}
        <section className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm sm:p-6">
          <div className="mb-5">
            <div className="flex items-center gap-2">
              <CheckCircle2
                size={19}
                className="text-[var(--primary)]"
              />
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                Strengths
              </h2>
            </div>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Areas where your learning history shows consistent strength.
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5">
            {['React', 'Python', 'SQL', 'Problem Solving', 'Project Building'].map(
              (skill) => (
                <div
                  key={skill}
                  className="rounded-full border border-[var(--border)] bg-[var(--surface-alt)] px-4 py-2 text-sm font-medium text-[var(--text-primary)]"
                >
                  {skill}
                </div>
              )
            )}
          </div>
        </section>

        {/* Active Friction Points */}
        <section className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm sm:p-6">
          <div className="mb-5">
            <div className="flex items-center gap-2">
              <CircleAlert
                size={19}
                className="text-[var(--feature-orange)]"
              />
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                Active Friction Points
              </h2>
            </div>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Topics where UniOS has noticed repeated difficulty.
            </p>
          </div>

          {frictionPoints.length === 0 ? (
            <EmptyState text="No active friction points right now." />
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {frictionPoints.map((memory) => (
                <MemoryCard
                  key={memory.id}
                  memory={memory}
                  onDelete={deleteMemory}
                />
              ))}
            </div>
          )}
        </section>


        {/* Recommended Revision Rails */}

<section className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm sm:p-6">
  <div className="mb-5">
    <div className="flex items-center gap-2">
      <Lightbulb
        size={19}
        className="text-[var(--feature-orange)]"
      />


  <h2 className="text-lg font-semibold text-[var(--text-primary)]">
    Recommended Revision
  </h2>
</div>

<p className="mt-1 text-sm text-[var(--text-secondary)]">
  Short revision tasks based on your recent learning friction points.
</p>

  </div>

{frictionPoints.length === 0 ? ( <EmptyState text="No revision recommendations right now." />
) : ( <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
{frictionPoints.map((point) => ( <div
       key={point.id}
       className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-5"
     > <div className="mb-4 flex items-start justify-between gap-3"> <div> <h3 className="text-sm font-semibold text-[var(--text-primary)]">
{point.title} </h3>

```
          <p className="mt-1 text-xs text-[var(--text-secondary)]">
            Seen {point.frequency} times
          </p>
        </div>

        <span className="rounded-full bg-[var(--primary-soft)] px-2.5 py-1 text-[11px] font-medium text-[var(--primary)]">
          Revise
        </span>
      </div>

      <p className="mb-4 text-sm leading-6 text-[var(--text-secondary)]">
        {point.description}
      </p>

      <button
        type="button"
        className="flex items-center gap-1.5 text-sm font-medium text-[var(--primary)] transition hover:text-[var(--primary-hover)]"
      >
        {point.title === 'SQL Joins'
          ? 'Practice SQL Joins'
          : point.title === 'Computer Networks'
            ? 'Revise Computer Networks'
            : `Review ${point.title}`}

        <ChevronRight size={15} />
      </button>
    </div>
  ))}
</div>


)}

</section>


        {/* AI Directives */}
        <section className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm sm:p-6">
          <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Lightbulb
                  size={19}
                  className="text-[var(--feature-orange)]"
                />
                <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                  AI Directives
                </h2>
              </div>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                Custom instructions that should influence how UniOS responds.
              </p>
            </div>

            {!isAddingDirective && (
              <button
                type="button"
                onClick={() => setIsAddingDirective(true)}
                className="flex w-fit items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[var(--primary-hover)]"
              >
                <Plus size={16} />
                Add Directive
              </button>
            )}
          </div>

          {isAddingDirective && (
            <div className="mb-4 rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4">
              <label
                htmlFor="new-directive"
                className="mb-2 block text-sm font-medium text-[var(--text-label)]"
              >
                New directive
              </label>

              <textarea
                id="new-directive"
                value={newDirective}
                onChange={(event) => setNewDirective(event.target.value)}
                placeholder="Example: Explain concepts using practical examples."
                rows={3}
                className="w-full resize-none rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)]"
              />

              <div className="mt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setIsAddingDirective(false);
                    setNewDirective('');
                  }}
                  className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--surface)]"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={addDirective}
                  className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
                >
                  Save Directive
                </button>
              </div>
            </div>
          )}

          <div className="space-y-3">
            {directives.length === 0 ? (
              <EmptyState text="No custom AI directives added." />
            ) : (
              directives.map((directive) => {
                const isEditing = editingDirectiveId === directive.id;

                return (
                  <div
                    key={directive.id}
                    className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4"
                  >
                    {isEditing ? (
                      <>
                        <textarea
                          value={editingText}
                          onChange={(event) =>
                            setEditingText(event.target.value)
                          }
                          rows={3}
                          className="w-full resize-none rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--primary)]"
                        />

                        <div className="mt-3 flex justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              setEditingDirectiveId(null);
                              setEditingText('');
                            }}
                            className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--surface)]"
                          >
                            Cancel
                          </button>

                          <button
                            type="button"
                            onClick={saveDirective}
                            className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)]"
                          >
                            Save
                          </button>
                        </div>
                      </>
                    ) : (
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3">
                          <div className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-[var(--primary)]" />

                          <p className="text-sm leading-6 text-[var(--text-primary)]">
                            {directive.text}
                          </p>
                        </div>

                        <div className="flex shrink-0 items-center gap-1">
                          <button
                            type="button"
                            onClick={() => startEditingDirective(directive)}
                            aria-label="Edit directive"
                            className="rounded-lg p-2 text-[var(--text-muted)] transition hover:bg-[var(--surface)] hover:text-[var(--text-primary)]"
                          >
                            <Edit3 size={16} />
                          </button>

                          <button
                            type="button"
                            onClick={() => deleteDirective(directive.id)}
                            aria-label="Delete directive"
                            className="rounded-lg p-2 text-[var(--text-muted)] transition hover:bg-[var(--danger-soft)] hover:text-[var(--danger-text)]"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </section>

        {/* Logged Memories */}
        <section className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm sm:p-6">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              Logged Memories
            </h2>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Individual observations created from your interactions with UniOS
              AI.
            </p>
          </div>

          {memories.length === 0 ? (
            <EmptyState text="No logged memories available." />
          ) : (
            <div className="space-y-3">
              {memories.map((memory) => (
                <MemoryCard
                  key={memory.id}
                  memory={memory}
                  onDelete={deleteMemory}
                  compact
                />
              ))}
            </div>
          )}
        </section>

        {/* Reset AI Context */}
        <section className="rounded-2xl border border-[var(--danger-border)] bg-[var(--danger-soft)] p-5 sm:p-6">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <RotateCcw
                  size={19}
                  className="text-[var(--danger-text)]"
                />

                <h2 className="text-lg font-semibold text-[var(--danger-text)]">
                  Reset AI Context
                </h2>
              </div>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
                Clear implicit memories and observed learning patterns.
                Your profile and preferences will remain unchanged.
              </p>
            </div>

            <button
              type="button"
              onClick={() => setShowResetModal(true)}
              className="flex shrink-0 items-center justify-center gap-2 rounded-lg border border-[var(--danger-border)] bg-[var(--surface)] px-4 py-2.5 text-sm font-medium text-[var(--danger-text)] transition hover:bg-white"
            >
              <RotateCcw size={16} />
              Reset AI Context
            </button>
          </div>
        </section>
      </div>

      {/* Reset Confirmation Modal */}
      {showResetModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-xl">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)]">
                  Reset AI context?
                </h3>

                <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                  This will remove your logged memories and active friction
                  points. Your profile, preferences and AI directives will stay
                  intact.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setShowResetModal(false)}
                aria-label="Close"
                className="rounded-lg p-1.5 text-[var(--text-muted)] hover:bg-[var(--surface-alt)] hover:text-[var(--text-primary)]"
              >
                <X size={18} />
              </button>
            </div>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowResetModal(false)}
                className="rounded-lg border border-[var(--border)] px-4 py-2.5 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-alt)]"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={resetAIContext}
                className="rounded-lg bg-[var(--danger-text)] px-4 py-2.5 text-sm font-medium text-white hover:opacity-90"
              >
                Reset Context
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

function ContextCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
        {label}
      </p>

      <p className="mt-2 text-sm font-semibold text-[var(--text-primary)]">
        {value}
      </p>

      <p className="mt-1 text-xs text-[var(--text-secondary)]">
        {detail}
      </p>
    </div>
  );
}

function MemoryCard({
  memory,
  onDelete,
  compact = false,
}: {
  memory: Memory;
  onDelete: (id: number) => void;
  compact?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] ${
        compact ? 'p-4' : 'p-5'
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">
              {memory.title}
            </h3>

            {!compact && (
              <span className="rounded-full bg-[var(--primary-soft)] px-2 py-0.5 text-[11px] font-medium text-[var(--primary)]">
                Active
              </span>
            )}
          </div>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            {memory.description}
          </p>

          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-muted)]">
            <span>Seen {memory.frequency} times</span>
            <span>Last observed: {memory.lastObserved}</span>
          </div>
        </div>

        <button
          type="button"
          onClick={() => onDelete(memory.id)}
          aria-label={`Delete ${memory.title}`}
          className="shrink-0 rounded-lg p-2 text-[var(--text-muted)] transition hover:bg-[var(--danger-soft)] hover:text-[var(--danger-text)]"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {!compact && (
        <button
          type="button"
          className="mt-4 flex items-center gap-1 text-xs font-medium text-[var(--primary)]"
        >
          View details
          <ChevronRight size={14} />
        </button>
      )}
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-alt)] px-5 py-8 text-center">
      <p className="text-sm text-[var(--text-muted)]">{text}</p>
    </div>
  );
}