
'use client';

import { useEffect, useMemo, useState } from 'react';

import type { Assessment } from '@/types/assessment';

import LessonRenderer from './LessonRenderer';
import MentorPanel from './mentor/MentorPanel';
import AssessmentPanel from './assessment/AssessmentPanel';

import { useLearning } from '@/hooks/useLearning';
import { generateAssessment } from '@/services/assessmentServices';
import { Check, ProgressRing } from '@/components/roadmap/UI';

interface LearningWorkspaceProps {
  topic: string;
  lessonId: string;
  roadmapId?: string;
  missionId?: string;
}

type WorkspacePanel = 'lesson' | 'mentor' | 'assessment';

const panels: { id: WorkspacePanel; label: string }[] = [
  { id: 'lesson', label: 'Lesson' },
  { id: 'mentor', label: 'Mentor' },
  { id: 'assessment', label: 'Assessment' },
];

export default function LearningWorkspace({
  topic,
  lessonId,
  roadmapId,
  missionId,
}: LearningWorkspaceProps) {
  const [activePanel, setActivePanel] =
    useState<WorkspacePanel>('lesson');

  const [saved, setSaved] = useState(false);

  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [isAssessmentLoading, setIsAssessmentLoading] = useState(false);
  const [assessmentError, setAssessmentError] = useState<string | null>(
    null,
  );
  const [assessmentRetryKey, setAssessmentRetryKey] = useState(0);

  // Keep the session input stable between renders.
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
    completedBlockIds,
    markBlockComplete,
    progress,
    isLoading,
    isSaving,
    error,
    syncCheckpoint,
  } = useLearning({
    session: learningSession,
  });

  // Load assessment when the assessment tab is opened.
  
useEffect(() => {
  if (activePanel !== 'assessment' || !sessionData?.id || assessment) {
    return;
  }

  const sessionId = sessionData.id;
  const sessionTopic = sessionData.topic || topic;

  let cancelled = false;

  async function loadAssessment() {
    setIsAssessmentLoading(true);
    setAssessmentError(null);

    try {
      const data = await generateAssessment({
        session_id: sessionId,
        topic: sessionTopic,
      });

      if (!cancelled) {
        setAssessment(data);
      }
    } catch (err) {
      if (!cancelled) {
        setAssessmentError(
          err instanceof Error
            ? err.message
            : 'Unable to load the assessment.',
        );
      }
    } finally {
      if (!cancelled) {
        setIsAssessmentLoading(false);
      }
    }
  }

  void loadAssessment();

  return () => {
    cancelled = true;
  };
}, [
  activePanel,
  sessionData,
  topic,
  assessment,
  assessmentRetryKey,
]);


  // Loading state.
  if (isLoading) {
    return (
      <main
        role="status"
        aria-live="polite"
        className="min-h-screen bg-[var(--background)]"
      >
        <div className="border-b border-[var(--border)] bg-[var(--surface)]">
          <div className="mx-auto w-full max-w-7xl space-y-2 px-4 py-4 sm:px-6">
            <div className="skeleton h-3 w-14 rounded-md" />
            <div className="skeleton h-5 w-56 max-w-full rounded-md" />
          </div>
        </div>

        <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6">
          <div className="flex items-center gap-3 text-sm text-[var(--text-secondary)]">
            <span className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
            Loading your learning session…
          </div>

          <div className="mt-6 space-y-4" aria-hidden="true">
            <div className="skeleton h-20 w-full rounded-3xl" />
            <div className="skeleton h-6 w-2/5 rounded-md" />
            <div className="skeleton h-4 w-full rounded-md" />
            <div className="skeleton h-4 w-5/6 rounded-md" />
            <div className="skeleton h-4 w-2/3 rounded-md" />
          </div>
        </div>
      </main>
    );
  }

  // Error or missing-data state.
  if (error || !lesson || !sessionData) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] p-4 sm:p-6">
        <section
          role="alert"
          className="rise w-full max-w-lg rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-8"
        >
          <div className="flex items-center gap-2.5">
            <span className="h-2 w-2 shrink-0 rounded-full bg-red-500" />

            <h1 className="text-xl font-semibold text-[var(--text-primary)]">
              Unable to load lesson
            </h1>
          </div>

          <p className="mt-2 pl-[18px] text-sm leading-6 text-[var(--text-secondary)]">
            {error ??
              'The backend did not return a lesson for this session.'}
          </p>

          <button
            type="button"
            onClick={() => window.location.reload()}
            className="ml-[18px] mt-5 rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
          >
            Try again
          </button>
        </section>
      </main>
    );
  }

  // sessionData is non-null after the guard above.
  const missionTitle = sessionData.topic || topic;

  const activeIndex = panels.findIndex(
    (panel) => panel.id === activePanel,
  );

  async function handleSaveProgress() {
    try {
      await syncCheckpoint();
      setSaved(true);
      window.setTimeout(() => setSaved(false), 2200);
    } catch {
      // The learning hook exposes the save error.
    }
  }

  function retryAssessment() {
    setAssessment(null);
    setAssessmentError(null);
    setAssessmentRetryKey((key) => key + 1);
  }

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Workspace header */}
      <header className="rise border-b border-[var(--border)] bg-[var(--surface)]">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-2 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6 sm:px-6">
          <div className="min-w-0">
            <p className="text-xs text-[var(--text-muted)]">Mission</p>

            <h1 className="mt-0.5 truncate text-lg font-semibold text-[var(--text-primary)]">
              {missionTitle}
            </h1>
          </div>

          <div className="min-w-0 sm:text-right">
            <p className="text-xs text-[var(--text-muted)]">
              Current lesson
            </p>

            <p className="mt-0.5 truncate text-sm font-medium text-[var(--text-primary)]">
              {lesson.title}
            </p>
          </div>
        </div>
      </header>

      {/* Workspace tabs */}
      <div className="sticky top-0 z-20 border-b border-[var(--border)] bg-[var(--surface)]">
        <div className="mx-auto w-full max-w-7xl px-4 py-3 sm:px-6">
          <div
            role="tablist"
            aria-label="Learning workspace"
            className="relative grid grid-cols-3 rounded-full bg-[var(--surface-alt)] p-1 sm:max-w-md"
          >
            <span
              aria-hidden="true"
              className="absolute inset-y-1 left-1 w-[calc((100%-0.5rem)/3)] rounded-full bg-[var(--primary)] shadow-sm transition-transform duration-300 ease-[cubic-bezier(0.3,1.2,0.5,1)]"
              style={{
                transform: `translateX(${activeIndex * 100}%)`,
              }}
            />

            {panels.map((panel) => {
              const active = activePanel === panel.id;

              return (
                <button
                  key={panel.id}
                  type="button"
                  role="tab"
                  id={`tab-${panel.id}`}
                  aria-selected={active}
                  aria-controls={`panel-${panel.id}`}
                  onClick={() => setActivePanel(panel.id)}
                  className={`relative z-10 rounded-full px-3 py-2 text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2 sm:px-4 ${
                    active
                      ? 'text-white'
                      : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  {panel.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
        <div
          
          role="tabpanel"
          id={`panel-${activePanel}`}
          aria-labelledby={`tab-${activePanel}`}
          className="rise"
        >
          {/* Lesson tab */}
          {activePanel === 'lesson' && (
            <div className="space-y-6">
              <section className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-4 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-5">
                <div className="flex flex-wrap items-center gap-4">
                  <ProgressRing
                    value={Math.round(progress)}
                    size={64}
                    stroke={6}
                  />

                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-[var(--text-primary)]">
                      Learning progress
                    </p>

                    <p className="mt-0.5 text-sm text-[var(--text-secondary)]">
                      {progress}% completed
                    </p>

                    <p className="mt-1 text-xs text-[var(--text-muted)]">
                      {completedBlockIds.length} of {lesson.blocks.length} blocks completed
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={handleSaveProgress}
                    disabled={isSaving}
                    className="inline-flex shrink-0 items-center gap-2 rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition hover:border-[var(--primary)] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                  >
                    {isSaving ? (
                      <>
                        <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
                        Saving…
                      </>
                    ) : saved ? (
                      <>
                        <Check className="text-[var(--primary)]" />
                        Saved
                      </>
                    ) : (
                      'Save progress'
                    )}
                  </button>
                </div>

                <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-[var(--surface-alt)]">
                  <div
                    className="h-full rounded-full bg-[var(--primary)] transition-[width] duration-700 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </section>

              <LessonRenderer
                lesson={lesson}
                completedBlockIds={completedBlockIds}
                onMarkBlockComplete={markBlockComplete}
              />

              {error && (
                <p
                  role="alert"
                  className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                >
                  {error}
                </p>
              )}
            </div>
          )}

          {/* Mentor tab */}
          {activePanel === 'mentor' && (
            <MentorPanel lesson={lesson} roadmapId={roadmapId} missionId={missionId}/>
          )}

          {/* Assessment tab */}
          <div hidden={activePanel !== 'assessment'}>
  <AssessmentPanel
    lesson={lesson}
    assessment={assessment}
    topic={sessionData.topic || topic}
    sessionId={sessionData.id}
    isLoading={isAssessmentLoading}
    loadError={assessmentError}
    onRetry={retryAssessment}
  />
</div>
        </div>
      </main>
    </div>
  );
}
