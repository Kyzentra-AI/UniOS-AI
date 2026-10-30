
'use client';

import { useCallback, useMemo, useRef, useState } from 'react';

import type {
  Assessment,
  AssessmentAttemptCreate,
  AssessmentAttemptResponse,
  AssessmentAnswerValue,
} from '@/types/assessment';

import { submitAssessmentAttempt } from '@/services/assessmentServices';

interface UseAssessmentOptions {
  assessment: Assessment;
  topic: string;
  sessionId?: string;
}

export function useAssessment({
  assessment,
  topic,
  sessionId,
}: UseAssessmentOptions) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] =
    useState<Record<string, AssessmentAnswerValue>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] =
    useState<AssessmentAttemptResponse | null>(null);

  const submissionInProgress = useRef(false);

  const startedAt = useMemo(() => Date.now(), []);

  const currentQuestion =
    assessment.questions[currentQuestionIndex] ?? null;

  const setAnswer = useCallback(
    (questionId: string, answer: AssessmentAnswerValue) => {
      if (submissionInProgress.current) return;

      setAnswers((previous) => ({
        ...previous,
        [questionId]: answer,
      }));
    },
    [],
  );

  const getAnswer = useCallback(
    (questionId: string) => answers[questionId] ?? '',
    [answers],
  );

  const goToQuestion = useCallback(
    (index: number) => {
      if (index < 0 || index >= assessment.questions.length) return;
      setCurrentQuestionIndex(index);
    },
    [assessment.questions.length],
  );

  const nextQuestion = useCallback(() => {
    setCurrentQuestionIndex((index) =>
      Math.min(index + 1, assessment.questions.length - 1),
    );
  }, [assessment.questions.length]);

  const previousQuestion = useCallback(() => {
    setCurrentQuestionIndex((index) => Math.max(0, index - 1));
  }, []);

  const buildAttempt = useCallback(
    (isCompleted = true): AssessmentAttemptCreate => ({
      session_id: sessionId,
      assessment_id: assessment.id,
      topic,
      answers: assessment.questions.map((question) => ({
        question_id: question.id,
        answer: answers[question.id] ?? '',
        hints_used: 0,
        time_spent_seconds: 0,
      })),
      total_time_spent_seconds: Math.max(
        0,
        Math.floor((Date.now() - startedAt) / 1000),
      ),
      is_completed: isCompleted,
    }),
    [sessionId, assessment, topic, answers, startedAt],
  );

  const submit = useCallback(async () => {
    if (submissionInProgress.current || result) {
      return result;
    }

    submissionInProgress.current = true;
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await submitAssessmentAttempt(buildAttempt(true));
      setResult(response);
      return response;
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unable to submit the assessment.';

      setError(message);
      throw err;
    } finally {
      submissionInProgress.current = false;
      setIsSubmitting(false);
    }
  }, [buildAttempt, result]);

  const reset = useCallback(() => {
    if (submissionInProgress.current) return;

    setCurrentQuestionIndex(0);
    setAnswers({});
    setError(null);
    setResult(null);
  }, []);

  return {
    currentQuestionIndex,
    currentQuestion,
    answers,
    isSubmitting,
    error,
    result,
    setAnswer,
    getAnswer,
    goToQuestion,
    nextQuestion,
    previousQuestion,
    buildAttempt,
    submit,
    reset,
  };
}
