
'use client';

import { useMemo, useState } from 'react';

import LessonRenderer from './LessonRenderer';
import MentorPanel from './mentor/MentorPanel';
import AssessmentPanel from './assessment/AssessmentPanel';

import { useLearning } from '@/hooks/useLearning';

interface LearningWorkspaceProps {
  topic: string;
  lessonId: string;
  roadmapId?: string;
  missionId?: string;
}

type WorkspacePanel = 'lesson' | 'mentor' | 'assessment';

export default function LearningWorkspace({
  topic,
  lessonId,
  roadmapId,
  missionId,
}: LearningWorkspaceProps) {
  const [activePanel, setActivePanel] =
    useState<WorkspacePanel>('lesson');

  // Keep the session object stable across rerenders.
  // This prevents useLearning's effect from repeatedly
  // creating sessions because of a new object reference.
  const learningSession = useMemo(
    () => ({
      topic,
      lesson_id: lessonId,
      roadmap_id: roadmapId,
      mission_id: missionId,
    }),
    [topic, lessonId, roadmapId, missionId],
  );

  const {
    sessionData,
    lesson,
    progress,
    isLoading,
    isSaving,
    error,
    syncCheckpoint,
  } = useLearning({
    session: learningSession,
  });

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] p-6">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />

          <p className="mt-4 text-sm text-[var(--text-secondary)]">
            Loading your learning session…
          </p>
        </div>
      </main>
    );
  }

  if (error || !lesson || !sessionData) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] p-6">
        <section className="w-full max-w-lg rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6">
          <h1 className="text-xl font-semibold text-[var(--text-primary)]">
            Unable to load lesson
          </h1>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            {error ??
              'The backend did not return a lesson for this session.'}
          </p>

          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-5 rounded-md bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white"
          >
            Try again
          </button>
        </section>
      </main>
    );
  }

  const missionTitle = sessionData.topic || topic;

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <header className="border-b border-[var(--border)] bg-[var(--surface)]">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-6 py-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
              Mission
            </p>

            <h1 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
              {missionTitle}
            </h1>
          </div>

          <div className="text-right">
            <p className="text-xs text-[var(--text-muted)]">
              Current Lesson
            </p>

            <p className="text-sm font-medium text-[var(--text-primary)]">
              {lesson.title}
            </p>
          </div>
        </div>
      </header>

      <div className="border-b border-[var(--border)] bg-[var(--surface)]">
        <div className="mx-auto flex w-full max-w-7xl gap-2 overflow-x-auto px-6 py-3">
          <button
            type="button"
            onClick={() => setActivePanel('lesson')}
            className={`rounded-md px-4 py-2 text-sm font-medium transition ${
              activePanel === 'lesson'
                ? 'bg-[var(--primary)] text-white'
                : 'text-[var(--text-secondary)] hover:bg-[var(--surface-alt)]'
            }`}
          >
            Lesson
          </button>

          <button
            type="button"
            onClick={() => setActivePanel('mentor')}
            className={`rounded-md px-4 py-2 text-sm font-medium transition ${
              activePanel === 'mentor'
                ? 'bg-[var(--primary)] text-white'
                : 'text-[var(--text-secondary)] hover:bg-[var(--surface-alt)]'
            }`}
          >
            Mentor
          </button>

          <button
            type="button"
            onClick={() => setActivePanel('assessment')}
            className={`rounded-md px-4 py-2 text-sm font-medium transition ${
              activePanel === 'assessment'
                ? 'bg-[var(--primary)] text-white'
                : 'text-[var(--text-secondary)] hover:bg-[var(--surface-alt)]'
            }`}
          >
            Assessment
          </button>
        </div>
      </div>

      <main className="mx-auto w-full max-w-7xl px-6 py-8">
        {activePanel === 'lesson' && (
          <div className="space-y-6">
            <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-[var(--text-primary)]">
                    Learning progress
                  </p>

                  <p className="mt-1 text-sm text-[var(--text-secondary)]">
                    {progress}% completed
                  </p>
                </div>

                <button
                  type="button"
                  onClick={async () => {
                    try {
                      await syncCheckpoint();
                    } catch {
                      // The hook exposes the error state.
                    }
                  }}
                  disabled={isSaving}
                  className="rounded-md border border-[var(--border)] px-4 py-2 text-sm font-medium text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSaving ? 'Saving…' : 'Save progress'}
                </button>
              </div>

              <div className="mt-3 h-2 overflow-hidden rounded-full bg-[var(--surface-alt)]">
                <div
                  className="h-full rounded-full bg-[var(--primary)] transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            <LessonRenderer lesson={lesson} />
          </div>
        )}

        {activePanel === 'mentor' && (
          <MentorPanel lesson={lesson} />
        )}

        {activePanel === 'assessment' && (
          <AssessmentPanel
            lesson={lesson}
            assessment={null}
            topic={sessionData.topic}
            sessionId={sessionData.id}
          />
        )}
      </main>
    </div>
  );
}
