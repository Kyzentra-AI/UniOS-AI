
'use client';

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';

import { useRouter } from 'next/navigation';

import Assessment, {
  type AssessmentAnswer,
  type AssessmentQuestion,
} from '@/components/Assessment';

import {
  ApiError,
  ApiTimeoutError,
} from '@/lib/api';

import {
  clearOnboardingDraft,
} from '@/stores/onboardingstore';

import { useOnboarding } from '@/hooks/useOnboarding';

type QuestionStatus =
  | 'idle'
  | 'processing'
  | 'pending_context'
  | 'success'
  | 'error';

type FailedOperation =
  | 'questions'
  | 'answers'
  | 'completion'
  | null;

interface AssessmentDraft {
  answers: Record<string, AssessmentAnswer>;
  currentIndex: number;
}

const POLLING_INTERVAL = 2000;

const ASSESSMENT_DRAFT_KEY =
  'unios_assessment_draft';

const ANALYSIS_MESSAGES = [
  'Aligning your profile with your academic background...',
  'Generating questions based on your learning goals...',
  'Preparing your personalized assessment...',
];

const RESOLVING_MESSAGES = [
  'Reviewing your assessment responses...',
  'Mapping your answers to your learning profile...',
  'Finalizing your personalized learning setup...',
];

const GENERATION_STAGES = [
  'Analyzing your academic profile',
  'Generating personalized assessment questions',
  'Preparing your assessment',
];

const RESOLUTION_STAGES = [
  'Reviewing your assessment responses',
  'Mapping your answers to your learning profile',
  'Finalizing your personalized setup',
];

function readAssessmentDraft(): AssessmentDraft {
  if (typeof window === 'undefined') {
    return {
      answers: {},
      currentIndex: 0,
    };
  }

  try {
    const stored = window.sessionStorage.getItem(
      ASSESSMENT_DRAFT_KEY
    );

    if (!stored) {
      return {
        answers: {},
        currentIndex: 0,
      };
    }

    const draft = JSON.parse(stored) as AssessmentDraft;

    return {
      answers:
        draft.answers &&
        typeof draft.answers === 'object'
          ? draft.answers
          : {},
      currentIndex:
        Number.isInteger(draft.currentIndex) &&
        draft.currentIndex >= 0
          ? draft.currentIndex
          : 0,
    };
  } catch (error) {
    console.error(
      'Unable to restore assessment draft:',
      error
    );

    return {
      answers: {},
      currentIndex: 0,
    };
  }
}

function saveAssessmentDraft(
  draft: AssessmentDraft
): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    window.sessionStorage.setItem(
      ASSESSMENT_DRAFT_KEY,
      JSON.stringify(draft)
    );
  } catch (error) {
    console.error(
      'Unable to save assessment draft:',
      error
    );
  }
}

function clearAssessmentDraft(): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    window.sessionStorage.removeItem(
      ASSESSMENT_DRAFT_KEY
    );
  } catch (error) {
    console.error(
      'Unable to clear assessment draft:',
      error
    );
  }
}

function ProgressStages({
  activeIndex,
  steps,
}: {
  activeIndex: number;
  steps: string[];
}) {
  return (
    <ol className="mt-6 space-y-4">
      {steps.map((step, index) => {
        const active = index === activeIndex;

        return (
          <li
            key={step}
            className="flex items-center gap-3"
          >
            <span
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border transition-all duration-300 ${
                active
                  ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                  : 'border-[var(--border)] text-[var(--text-muted)]'
              }`}
            >
              {active ? (
                <span className="h-3 w-3 animate-pulse rounded-full bg-[var(--primary)]" />
              ) : (
                <span className="text-xs font-semibold">
                  {index + 1}
                </span>
              )}
            </span>

            <span
              className={`text-sm transition-colors ${
                active
                  ? 'font-semibold text-[var(--text-primary)]'
                  : 'text-[var(--text-muted)]'
              }`}
            >
              {step}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

export default function AssessmentPage() {
  const router = useRouter();

  const {
    getKIEQuestions,
    submitKIEAnswers,
    completeOnboarding,
    isGettingQuestions,
    isSubmittingAnswers,
    isCompleting,
    questionsError,
    answersError,
    completeError,
  } = useOnboarding();

  const [questions, setQuestions] = useState<
    AssessmentQuestion[]
  >([]);

  const [status, setStatus] =
    useState<QuestionStatus>('idle');

  const [errorMessage, setErrorMessage] =
    useState('');

  const [failedOperation, setFailedOperation] =
    useState<FailedOperation>(null);

  const [pollAttempt, setPollAttempt] = useState(0);

  const [isResolving, setIsResolving] =
    useState(false);

  const [loadingMessageIndex, setLoadingMessageIndex] =
    useState(0);

  const [assessmentDraft, setAssessmentDraft] =
    useState<AssessmentDraft>(() => readAssessmentDraft());

  const requestInFlight = useRef(false);

  const completionStarted = useRef(false);

  const pendingAnswersRef = useRef<
    Record<string, AssessmentAnswer> | null
  >(null);

  const loadingMessages = isResolving
    ? RESOLVING_MESSAGES
    : ANALYSIS_MESSAGES;

  const progressStages = isResolving
    ? RESOLUTION_STAGES
    : GENERATION_STAGES;

  const loadQuestions = useCallback(async () => {
    if (requestInFlight.current) {
      return;
    }

    requestInFlight.current = true;

    try {
      setErrorMessage('');

      const response = await getKIEQuestions();

      if (response.status === 'pending_context') {
        setQuestions(response.questions);
        setStatus('pending_context');
        setFailedOperation(null);
        return;
      }

      if (response.status === 'success') {
        setStatus('success');
        setFailedOperation(null);
        return;
      }

      if (response.status === 'processing') {
        setStatus('processing');
        setPollAttempt((previous) => previous + 1);
        return;
      }

      setStatus('error');
      setFailedOperation('questions');

      setErrorMessage(
        'Unexpected response from onboarding service.'
      );
    } catch (error) {
      console.error(
        'Failed to load KIE questions:',
        error
      );

      if (
        error instanceof ApiTimeoutError ||
        error instanceof TypeError
      ) {
        setStatus('processing');
        setFailedOperation('questions');

        setErrorMessage(
          'The status request took too long. Your setup may still be processing.'
        );

        setPollAttempt((previous) => previous + 1);
        return;
      }

      setStatus('error');
      setFailedOperation('questions');

      setErrorMessage(
        error instanceof ApiError
          ? error.message
          : 'Unable to load onboarding questions.'
      );
    } finally {
      requestInFlight.current = false;
    }
  }, [getKIEQuestions]);

  useEffect(() => {
    void loadQuestions();
  }, [loadQuestions]);

  useEffect(() => {
    if (status !== 'processing') {
      return;
    }

    const timeout = window.setTimeout(() => {
      void loadQuestions();
    }, POLLING_INTERVAL);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [status, pollAttempt, loadQuestions]);

  useEffect(() => {
    if (status !== 'processing') {
      setLoadingMessageIndex(0);
      return;
    }

    const interval = window.setInterval(() => {
      setLoadingMessageIndex((previous) =>
        (previous + 1) % loadingMessages.length
      );
    }, 4000);

    return () => {
      window.clearInterval(interval);
    };
  }, [status, loadingMessages.length]);

  const handleCompleteOnboarding =
    useCallback(async () => {
      if (completionStarted.current) {
        return;
      }

      completionStarted.current = true;

      try {
        setErrorMessage('');
        setFailedOperation(null);

        await completeOnboarding();

        clearAssessmentDraft();
        clearOnboardingDraft();

        router.push('/syllabus');
      } catch (error) {
        console.error(
          'Failed to complete onboarding:',
          error
        );

        completionStarted.current = false;

        setStatus('error');
        setFailedOperation('completion');

        setErrorMessage(
          error instanceof Error
            ? error.message
            : 'KIE finished processing, but onboarding could not be completed.'
        );
      }
    }, [completeOnboarding, router]);

  useEffect(() => {
    if (status !== 'success') {
      return;
    }

    void handleCompleteOnboarding();
  }, [status, handleCompleteOnboarding]);

  const postAnswers = useCallback(
    async (
      answers: Record<string, AssessmentAnswer>
    ) => {
      const payload = {
        answers: Object.entries(answers).map(
          ([questionId, answer]) => ({
            question_id: questionId,
            answer,
          })
        ),
      };

      pendingAnswersRef.current = answers;

      saveAssessmentDraft({
        answers,
        currentIndex: assessmentDraft.currentIndex,
      });

      try {
        setErrorMessage('');
        setFailedOperation(null);

        await submitKIEAnswers(payload);

        setQuestions([]);
        setIsResolving(true);
        setLoadingMessageIndex(0);
        setStatus('processing');
        setPollAttempt((previous) => previous + 1);
      } catch (error) {
        console.error(
          'Failed to submit KIE answers:',
          error
        );

        setFailedOperation('answers');
        setStatus('error');

        setErrorMessage(
          error instanceof Error
            ? error.message
            : 'Unable to submit your answers. Your answers have been saved.'
        );
      }
    },
    [
      submitKIEAnswers,
      assessmentDraft.currentIndex,
    ]
  );

  const handleSubmit = async (
    answers: Record<string, AssessmentAnswer>
  ) => {
    pendingAnswersRef.current = answers;

    const nextDraft = {
      answers,
      currentIndex: assessmentDraft.currentIndex,
    };

    setAssessmentDraft(nextDraft);
    saveAssessmentDraft(nextDraft);

    await postAnswers(answers);
  };

  const handleAssessmentDraftChange = useCallback(
    (
      answers: Record<string, AssessmentAnswer>,
      currentIndex: number
    ) => {
      const nextDraft = {
        answers,
        currentIndex,
      };

      setAssessmentDraft(nextDraft);
      saveAssessmentDraft(nextDraft);
    },
    []
  );

  const handleRetry = async () => {
    setErrorMessage('');

    if (failedOperation === 'completion') {
      setStatus('success');
      void handleCompleteOnboarding();
      return;
    }

    if (failedOperation === 'answers') {
      try {
        const response = await getKIEQuestions();

        if (response.status === 'success') {
          setStatus('success');
          setFailedOperation(null);
          return;
        }

        if (response.status === 'processing') {
          setIsResolving(true);
          setLoadingMessageIndex(0);
          setStatus('processing');
          setFailedOperation(null);
          setPollAttempt((previous) => previous + 1);
          return;
        }

        if (response.status === 'pending_context') {
          setQuestions(response.questions);

          const answers =
            pendingAnswersRef.current ??
            assessmentDraft.answers;

          if (Object.keys(answers).length === 0) {
            setStatus('pending_context');
            setFailedOperation(null);
            return;
          }

          setStatus('pending_context');
          await postAnswers(answers);
          return;
        }

        setStatus('error');
        setFailedOperation('answers');

        setErrorMessage(
          'Unable to determine the assessment status. Please retry.'
        );
      } catch (error) {
        setStatus('error');
        setFailedOperation('answers');

        setErrorMessage(
          error instanceof Error
            ? error.message
            : 'Unable to check assessment status.'
        );
      }

      return;
    }

    setFailedOperation(null);
    setStatus('idle');

    await loadQuestions();
  };

  const isLoadingQuestions =
    isGettingQuestions ||
    status === 'processing';

  if (
    isLoadingQuestions &&
    status !== 'pending_context'
  ) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center px-6 py-10">
        <div
          role="status"
          aria-live="polite"
          className="w-full max-w-lg rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm sm:p-8"
        >
          <div className="mb-6 flex items-center gap-4">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[var(--primary-soft)]">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
            </span>

            <div>
              <h1 className="text-xl font-semibold text-[var(--text-primary)]">
                {isResolving
                  ? 'Analyzing your responses'
                  : 'Personalizing your experience'}
              </h1>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                {isResolving
                  ? 'Building your personalized learning profile.'
                  : 'Preparing your personalized assessment.'}
              </p>
            </div>
          </div>

          <div className="rounded-xl bg-[var(--background)] p-4">
            <p
              className="text-sm font-medium leading-6 text-[var(--text-primary)]"
              aria-live="polite"
            >
              {loadingMessages[loadingMessageIndex]}
            </p>
          </div>

          <div className="mt-6 border-t border-[var(--border)] pt-6">
            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              {isResolving
                ? 'Finalization stages · Indicative'
                : 'Assessment generation · Indicative'}
            </p>

            <ProgressStages
              activeIndex={loadingMessageIndex}
              steps={progressStages}
            />
          </div>

          <p className="mt-6 border-t border-[var(--border)] pt-4 text-xs leading-5 text-[var(--text-muted)]">
            These stages provide an indication of the work underway. Actual completion is determined by the onboarding service.
          </p>

          {errorMessage && (
            <div className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--background)] p-4">
              <p className="text-sm text-[var(--text-secondary)]">
                {errorMessage}
              </p>

              <button
                type="button"
                onClick={handleRetry}
                disabled={isGettingQuestions}
                className="mt-3 rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                Check status again
              </button>
            </div>
          )}
        </div>
      </main>
    );
  }

  if (status === 'pending_context') {
    return (
      <main className="min-h-[70vh] px-6 py-10">
        <Assessment
          questions={questions}
          onSubmit={handleSubmit}
          isSubmitting={isSubmittingAnswers}
          initialAnswers={assessmentDraft.answers}
          initialIndex={assessmentDraft.currentIndex}
          onDraftChange={handleAssessmentDraftChange}
        />
      </main>
    );
  }

  if (status === 'success') {
    return (
      <main className="flex min-h-[70vh] items-center justify-center px-6">
        <div
          role="status"
          aria-live="polite"
          className="w-full max-w-md rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 text-center shadow-sm sm:p-8"
        >
          <div className="mx-auto mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--primary-soft)]">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
          </div>

          <h1 className="text-xl font-semibold text-[var(--text-primary)]">
            Completing your onboarding
          </h1>

          <p className="mt-2 text-sm text-[var(--text-secondary)]">
            Your personalized experience is being prepared.
          </p>
        </div>
      </main>
    );
  }

  if (status === 'error') {
    return (
      <main className="flex min-h-[70vh] items-center justify-center px-6">
        <div className="w-full max-w-md text-center">
          <h1 className="text-xl font-semibold text-[var(--text-primary)]">
            Something went wrong
          </h1>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            {errorMessage ||
              questionsError?.message ||
              answersError?.message ||
              completeError?.message ||
              'Please try again.'}
          </p>

          <button
            type="button"
            onClick={handleRetry}
            disabled={isCompleting || isSubmittingAnswers}
            className="mt-6 rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {failedOperation === 'completion'
              ? 'Retry completion'
              : failedOperation === 'answers'
                ? 'Retry assessment submission'
                : 'Try again'}
          </button>
        </div>
      </main>
    );
  }

  return null;
}
