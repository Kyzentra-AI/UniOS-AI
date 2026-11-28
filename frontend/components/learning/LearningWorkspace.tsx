
'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';

import type { Assessment } from '@/types/assessment';

import LessonRenderer from './LessonRenderer';
import MentorPanel from './mentor/MentorPanel';
import AssessmentPanel from './assessment/AssessmentPanel';

import { useLearning } from '@/hooks/useLearning';
import { generateAssessment } from '@/services/assessmentServices';
import { Check, ProgressRing } from '@/components/roadmap/UI';
import Link from 'next/link';

interface LearningWorkspaceProps {
  topic: string;
  lessonId: string;
  roadmapId?: string;
  missionId?: string;
}

type WorkspacePanel = 'lesson' | 'assessment';

const panels: { id: WorkspacePanel; label: string }[] = [
  { id: 'lesson', label: 'Lesson & Tutor' },
  { id: 'assessment', label: 'Assessment' },
];

export default function LearningWorkspace({
  topic,
  lessonId,
  roadmapId,
  missionId,
}: LearningWorkspaceProps) {
  const router = useRouter();

  const [activePanel, setActivePanel] =
    useState<WorkspacePanel>('lesson');

  const [saved, setSaved] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  const [isFinishingLesson, setIsFinishingLesson] = useState(false);
  const [completionError, setCompletionError] = useState<string | null>(
    null,
  );

  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [isAssessmentLoading, setIsAssessmentLoading] = useState(false);
  const [assessmentError, setAssessmentError] = useState<string | null>(
    null,
  );
  const [assessmentRetryKey, setAssessmentRetryKey] = useState(0);
  const [forceRetake, setForceRetake] = useState(false);

  // Prevent duplicate pause requests from pagehide + popstate.
  const pauseStartedRef = useRef(false);

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
    currentBlockIndex,
    completedBlockIds,
    markBlockComplete,
    progress,
    isLoading,
    isSaving,
    error,
    syncCheckpoint,
    pauseSession,
    pauseSessionOnExit,
    completeSession,
    nextBlock,
    previousBlock,
  } = useLearning({
    session: learningSession,
  });

  const sessionCompleted = sessionData?.status === 'COMPLETED';

  // Best-effort pause when the user closes the tab or uses browser Back.
  useEffect(() => {
    const handlePageExit = () => {
      if (pauseStartedRef.current || sessionCompleted) {
        return;
      }

      pauseStartedRef.current = true;
      pauseSessionOnExit();
    };

    window.addEventListener('pagehide', handlePageExit);
    window.addEventListener('popstate', handlePageExit);

    return () => {
      window.removeEventListener('pagehide', handlePageExit);
      window.removeEventListener('popstate', handlePageExit);
    };
  }, [pauseSessionOnExit, sessionCompleted]);

  // Generate/load assessment only after the backend confirms completion.
  useEffect(() => {
    if (
      activePanel !== 'assessment' ||
      !sessionCompleted ||
      !sessionData?.id ||
      assessment
    ) {
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
          ...(forceRetake ? { force_retake: true } : {}),
        });

        if (!cancelled) {
          setAssessment(data);
          setForceRetake(false);
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
    sessionCompleted,
    sessionData,
    topic,
    assessment,
    assessmentRetryKey,
    forceRetake,
  ]);

  async function handleSaveProgress() {
    try {
      await syncCheckpoint();
      setSaved(true);
      window.setTimeout(() => setSaved(false), 2200);
    } catch {
      // The learning hook exposes the save error.
    }
  }

  async function handlePauseAndExit() {
    if (
      isExiting ||
      isSaving ||
      isFinishingLesson ||
      !sessionData ||
      sessionCompleted
    ) {
      return;
    }

    setIsExiting(true);
    pauseStartedRef.current = true;

    try {
      await pauseSession();

      if (missionId) {
        router.push(`/missions/${encodeURIComponent(missionId)}`);
      } else {
        router.push('/missions');
      }
    } catch {
      pauseStartedRef.current = false;
      setIsExiting(false);
    }
  }

  // Complete the backend session before opening the assessment panel.
  async function handleFinishLesson() {
    if (
      isFinishingLesson ||
      isSaving ||
      !sessionData ||
      !lesson ||
      progress < 100
    ) {
      return;
    }

    setIsFinishingLesson(true);
    setCompletionError(null);

    try {
      await completeSession();

      setAssessment(null);
      setAssessmentError(null);
      setForceRetake(false);

      setActivePanel('assessment');
    } catch (err) {
      setCompletionError(
        err instanceof Error
          ? err.message
          : 'Unable to complete the lesson. Please try again.',
      );
    } finally {
      setIsFinishingLesson(false);
    }
  }

  // Retry normal assessment generation after a loading error or empty response.
  function retryAssessment() {
    if (isAssessmentLoading) return;

    setAssessment(null);
    setAssessmentError(null);
    setAssessmentRetryKey((key) => key + 1);
  }

  // Explicitly request a fresh assessment from the backend.
  function handleRetakeAssessment() {
    if (isAssessmentLoading) return;

    setAssessment(null);
    setAssessmentError(null);
    setForceRetake(true);
    setAssessmentRetryKey((key) => key + 1);
  }

  const missionTitle = sessionData?.topic || topic;

  const activeIndex = panels.findIndex(
    (panel) => panel.id === activePanel,
  );

  // Loading state.
  if (isLoading) {
    return (
      <main
        role="status"
        aria-live="polite"
        className="flex h-dvh flex-col overflow-hidden bg-[var(--background)]"
      >
        <header className="shrink-0 border-b border-[var(--border)] bg-[var(--surface)]">
          <div className="mx-auto w-full max-w-7xl space-y-2 px-4 py-4 sm:px-6">
            <div className="skeleton h-3 w-14 rounded-md" />
            <div className="skeleton h-5 w-56 max-w-full rounded-md" />
          </div>
        </header>

        <div className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">
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
      <main className="flex h-dvh items-center justify-center overflow-y-auto bg-[var(--background)] p-4 sm:p-6">
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
          {error?.toLowerCase().includes('insufficient') &&
  error.toLowerCase().includes('credit') && (
    <Link
      href="/billing"
      className="ml-[18px] mt-3 inline-flex rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)]"
    >
      Buy Plans
    </Link>
  )}
        </section>
      </main>
    );
  }

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-[var(--background)]">
      {/* Compact workspace top bar */}
      <header className="z-30 shrink-0 border-b border-[var(--border)] bg-[var(--surface)]">
        <div className="flex min-h-[68px] flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <div className="min-w-0">
              <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--text-muted)]">
                Learning Workspace
              </p>

              <h1 className="mt-0.5 truncate text-sm font-semibold text-[var(--text-primary)] sm:text-base">
                {missionTitle}
              </h1>
            </div>

            <span className="hidden h-8 w-px shrink-0 bg-[var(--border)] sm:block" />

            <div className="hidden min-w-0 sm:block">
              <p className="text-[11px] text-[var(--text-muted)]">
                Current lesson
              </p>

              <p className="mt-0.5 max-w-[260px] truncate text-sm font-medium text-[var(--text-secondary)]">
                {lesson.title}
              </p>
            </div>
          </div>

          {/* Workspace tabs */}
          <div
            role="tablist"
            aria-label="Learning workspace"
            className="relative grid w-full grid-cols-2 rounded-full bg-[var(--surface-alt)] p-1 sm:w-[280px]"
          >
            <span
              aria-hidden="true"
              className="absolute inset-y-1 left-1 w-[calc((100%-0.5rem)/2)] rounded-full bg-[var(--primary)] shadow-sm transition-transform duration-300 ease-[cubic-bezier(0.3,1.2,0.5,1)]"
              style={{
                transform: `translateX(${activeIndex * 100}%)`,
              }}
            />

            {panels.map((panel) => {
              const active = activePanel === panel.id;
              const locked =
                panel.id === 'assessment' && !sessionCompleted;

              return (
                <button
                  key={panel.id}
                  type="button"
                  role="tab"
                  id={`tab-${panel.id}`}
                  aria-selected={active}
                  aria-controls={`panel-${panel.id}`}
                  aria-disabled={locked}
                  disabled={locked}
                  onClick={() => {
                    if (!locked) {
                      setActivePanel(panel.id);
                    }
                  }}
                  title={
                    locked
                      ? 'Complete the lesson before opening the assessment.'
                      : undefined
                  }
                  className={`relative z-10 rounded-full px-3 py-2 text-xs font-semibold transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2 sm:text-sm ${
                    active
                      ? 'text-white'
                      : locked
                        ? 'cursor-not-allowed text-[var(--text-muted)] opacity-60'
                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  {panel.label}
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main workspace area */}
      <main className="min-h-0 flex-1 overflow-y-auto lg:overflow-hidden">
        {/* Lesson and AI Mentor panel */}
        <div
          role="tabpanel"
          id="panel-lesson"
          aria-labelledby="tab-lesson"
          hidden={activePanel !== 'lesson'}
          className="min-h-0 lg:h-full"
        >
          <div className="grid grid-cols-1 gap-4 p-3 sm:gap-5 sm:p-5 lg:h-full lg:min-h-0 lg:grid-cols-[minmax(0,1fr)_400px] lg:gap-5 lg:p-5">
            {/* Left: Lesson reader */}
            <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_28px_rgba(24,52,58,0.04)] lg:h-full">
              {/* Lesson progress header */}
              <div className="shrink-0 border-b border-[var(--border)] px-4 py-3 sm:px-5">
                <div className="flex items-center gap-3">
                  <ProgressRing
                    value={Math.round(progress)}
                    size={48}
                    stroke={5}
                  />

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-[var(--text-primary)]">
                        Lesson progress
                      </p>

                      <p className="text-xs font-medium text-[var(--text-secondary)]">
                        {Math.round(progress)}%
                      </p>
                    </div>

                    <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-[var(--surface-alt)]">
                      <div
                        className="h-full rounded-full bg-[var(--primary)] transition-[width] duration-700 ease-out"
                        style={{
                          width: `${Math.min(100, Math.max(0, progress))}%`,
                        }}
                      />
                    </div>

                    <p className="mt-1.5 text-xs text-[var(--text-muted)]">
                      {completedBlockIds.length} of {lesson.blocks.length} sections completed
                    </p>
                  </div>
                </div>
              </div>

              {/* Mobile: natural page scroll.
                  Desktop: independent lesson scroll. */}
              <div className="min-h-0 px-3 py-4 sm:px-5 sm:py-5 lg:flex-1 lg:overflow-y-auto lg:overscroll-contain">
                <LessonRenderer
                  lesson={lesson}
                  completedBlockIds={completedBlockIds}
                  currentBlockIndex={currentBlockIndex}
                  isSaving={isSaving || isExiting}
                  isCompleting={isFinishingLesson}
                  onMarkBlockComplete={markBlockComplete}
                  onPreviousBlock={previousBlock}
                  onNextBlock={nextBlock}
                  onFinishLesson={handleFinishLesson}
                />

                {error && (
                  <p
                    role="alert"
                    className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                  >
                    {error}
                  </p>
                )}

                {completionError && (
                  <p
                    role="alert"
                    className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                  >
                    {completionError}
                  </p>
                )}
              </div>

              {/* Persistent left-side workspace footer */}
              <footer className="z-10 shrink-0 border-t border-[var(--border)] bg-[var(--surface)] px-4 py-3 sm:px-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="hidden text-xs text-[var(--text-muted)] sm:block">
                    Your learning progress is saved to this session.
                  </p>

                  <div className="ml-auto flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={handleSaveProgress}
                      disabled={
                        isSaving ||
                        isExiting ||
                        isFinishingLesson ||
                        sessionCompleted
                      }
                      className="inline-flex shrink-0 items-center gap-2 rounded-xl border border-[var(--border)] px-3 py-2.5 text-xs font-semibold text-[var(--text-primary)] transition hover:border-[var(--primary)] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] sm:px-4 sm:text-sm"
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

                    <button
                      type="button"
                      onClick={handlePauseAndExit}
                      disabled={
                        isSaving ||
                        isExiting ||
                        isFinishingLesson ||
                        sessionCompleted
                      }
                      className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-[var(--primary)] px-3 py-2.5 text-xs font-semibold text-white transition hover:bg-[var(--primary-hover)] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2 sm:px-4 sm:text-sm"
                    >
                      {isExiting ? (
                        <>
                          <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
                          Pausing…
                        </>
                      ) : (
                        'Pause & Exit'
                      )}
                    </button>
                  </div>
                </div>
              </footer>
            </section>

            {/* Right: AI Mentor */}
            <aside className="flex h-[650px] min-h-[650px] min-w-0 flex-col lg:h-full lg:min-h-0">
              <MentorPanel
                lesson={lesson}
                roadmapId={roadmapId}
                missionId={missionId}
                currentBlockIndex={currentBlockIndex}
                subject={sessionData.topic || topic}
              />
            </aside>
          </div>
        </div>

        {/* Assessment workspace */}
        <div
          role="tabpanel"
          id="panel-assessment"
          aria-labelledby="tab-assessment"
          hidden={activePanel !== 'assessment'}
          className="min-h-0 overflow-visible p-3 sm:p-5 lg:h-full lg:overflow-y-auto"
        >
          <div className="mx-auto w-full max-w-5xl">
            <AssessmentPanel
              lesson={lesson}
              assessment={assessment}
              topic={sessionData.topic || topic}
              sessionId={sessionData.id}
              isLoading={isAssessmentLoading}
              loadError={assessmentError}
              onRetry={retryAssessment}
              onRetake={handleRetakeAssessment}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
