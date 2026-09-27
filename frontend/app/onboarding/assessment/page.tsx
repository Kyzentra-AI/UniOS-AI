'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import Assessment, {
  type AssessmentAnswer,
  type AssessmentQuestion,
} from '@/components/Assessment';

import { useOnboarding } from '@/hooks/useOnboarding';

type QuestionStatus =
  | 'idle'
  | 'processing'
  | 'pending_context'
  | 'success'
  | 'error';

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

  const loadQuestions = useCallback(async () => {
    try {
      setErrorMessage('');

      const response = await getKIEQuestions();

      const responseStatus =
        response.status as string;

      // KIE has generated the questions
      if (response.status === 'pending_context') {
        setQuestions(response.questions);
        setStatus('pending_context');
        return;
      }

      // KIE has finished resolving the answers
      if (responseStatus === 'success') {
        setStatus('success');
        return;
      }

      // KIE is still processing
      if (responseStatus === 'processing') {
        setStatus('processing');
        return;
      }

      setStatus('error');

      setErrorMessage(
        'Unexpected response from onboarding service.'
      );
    } catch (error) {
      console.error(
        'Failed to load KIE questions:',
        error
      );

      setStatus('error');

      setErrorMessage(
        'Unable to load onboarding questions.'
      );
    }
  }, [getKIEQuestions]);

  // Initial question/status check
  useEffect(() => {
    void loadQuestions();
  }, [loadQuestions]);

  // Poll only while KIE is processing
  useEffect(() => {
    if (status !== 'processing') {
      return;
    }

    const timeout = window.setTimeout(() => {
      void loadQuestions();
    }, 2000);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [status, loadQuestions]);

  // Once KIE is successful, complete onboarding
  const handleCompleteOnboarding =
    useCallback(async () => {
      try {
        setErrorMessage('');

        await completeOnboarding();

        router.push('/onboarding');
      } catch (error) {
        console.error(
          'Failed to complete onboarding:',
          error
        );

        setStatus('error');

        setErrorMessage(
          'KIE finished processing, but onboarding could not be completed.'
        );
      }
    }, [completeOnboarding, router]);

  useEffect(() => {
    if (status !== 'success') {
      return;
    }

    void handleCompleteOnboarding();
  }, [status, handleCompleteOnboarding]);

  const handleSubmit = async (
    answers: Record<
      string,
      AssessmentAnswer
    >
  ) => {
    try {
      setErrorMessage('');

      const payload = {
        answers: Object.entries(answers).map(
          ([questionId, answer]) => ({
            question_id: questionId,
            answer,
          })
        ),
      };

      await submitKIEAnswers(payload);

      // Backend moves to KIE_RESOLVING.
      // Start polling again.
      setStatus('processing');
      setQuestions([]);
    } catch (error) {
      console.error(
        'Failed to submit KIE answers:',
        error
      );

      setStatus('error');

      setErrorMessage(
        'Unable to submit your answers. Please try again.'
      );
    }
  };

  const isLoadingQuestions =
    isGettingQuestions ||
    status === 'processing';

  const isSubmitting =
    isSubmittingAnswers;

  if (
    isLoadingQuestions &&
    status !== 'pending_context'
  ) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center px-6">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto mb-5 h-8 w-8 animate-spin rounded-full border-2 border-neutral-200 border-t-neutral-900" />

          <h1 className="text-xl font-semibold text-neutral-900">
            Personalizing your experience
          </h1>

          <p className="mt-2 text-sm leading-6 text-neutral-500">
            We are analyzing your profile and
            preparing a few questions for you.
          </p>
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
          isSubmitting={isSubmitting}
        />
      </main>
    );
  }

  if (status === 'success') {
    return (
      <main className="flex min-h-[70vh] items-center justify-center px-6">
        <div className="text-center">
          <div className="mx-auto mb-5 h-8 w-8 animate-spin rounded-full border-2 border-neutral-200 border-t-neutral-900" />

          <h1 className="text-xl font-semibold text-neutral-900">
            Completing your onboarding
          </h1>

          <p className="mt-2 text-sm text-neutral-500">
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
          <h1 className="text-xl font-semibold text-neutral-900">
            Something went wrong
          </h1>

          <p className="mt-2 text-sm leading-6 text-neutral-500">
            {errorMessage ||
              questionsError?.message ||
              answersError?.message ||
              completeError?.message ||
              'Please try again.'}
          </p>

          <button
            type="button"
            onClick={() => {
              setStatus('idle');
              void loadQuestions();
            }}
            disabled={isCompleting}
            className="mt-6 rounded-xl bg-neutral-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Try again
          </button>
        </div>
      </main>
    );
  }

  return null;
}