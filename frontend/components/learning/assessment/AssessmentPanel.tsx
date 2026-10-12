'use client';

import { useEffect, useState } from 'react';
import type { Lesson } from '@/types/learning';
import type { Assessment } from '@/types/assessment';
import { useAssessment } from '@/hooks/useAssessment';

interface AssessmentPanelProps {
  lesson: Lesson;
  assessment?: Assessment | null;
  topic: string;
  sessionId?: string;
}

export default function AssessmentPanel({
  lesson,
  assessment,
  topic,
  sessionId,
}: AssessmentPanelProps) {
  if (!assessment || assessment.questions.length === 0) {
    return (
      <section className="rounded-xl border border-gray-200 p-6">
        <h2 className="text-xl font-semibold">
          Check your understanding
        </h2>

        <p className="mt-2 text-sm text-gray-500">
          Assessment for {lesson.title}
        </p>

        <p className="mt-5 rounded-lg bg-gray-50 p-4 text-sm text-gray-600">
          No assessment questions are available yet.
        </p>
      </section>
    );
  }

  return (
    <AssessmentForm
      assessment={assessment}
      topic={topic}
      sessionId={sessionId}
      lessonTitle={lesson.title}
    />
  );
}

function AssessmentForm({
  assessment,
  topic,
  sessionId,
  lessonTitle,
}: {
  assessment: Assessment;
  topic: string;
  sessionId?: string;
  lessonTitle: string;
}) {
  const {
    currentQuestionIndex,
    currentQuestion,
    isSubmitting,
    error,
    result,
    setAnswer,
    getAnswer,
    nextQuestion,
    previousQuestion,
    submit,
  } = useAssessment({ assessment, topic, sessionId });

  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    setSubmitError(null);
  }, [currentQuestionIndex]);

  const isLastQuestion =
    currentQuestionIndex === assessment.questions.length - 1;

  const answeredCount = assessment.questions.filter((question) => {
    const answer = getAnswer(question.id);

    if (Array.isArray(answer)) return answer.length > 0;
    if (typeof answer === 'object' && answer !== null) {
      return Object.keys(answer).length > 0;
    }

    return String(answer).trim().length > 0;
  }).length;

  async function handleSubmit() {
    setSubmitError(null);

    try {
      await submit();
    } catch {
      setSubmitError('Your assessment could not be submitted. Please try again.');
    }
  }

  if (result) {
    return (
      <section className="rounded-xl border border-gray-200 p-6">
        <h2 className="text-xl font-semibold">Assessment results</h2>

        <p className="mt-2 text-sm text-gray-500">
          {lessonTitle}
        </p>

        {result.score != null && (
          <p className="mt-5 text-2xl font-bold">
            Score: {result.score}
          </p>
        )}

        <p className="mt-3 text-sm text-gray-600">
          {result.feedback ?? 'Your assessment has been submitted.'}
        </p>

        {result.mastery_updates && (
          <pre className="mt-4 overflow-x-auto rounded-lg bg-gray-50 p-3 text-xs">
            {JSON.stringify(result.mastery_updates, null, 2)}
          </pre>
        )}
      </section>
    );
  }

  if (!currentQuestion) return null;

  const currentAnswer = getAnswer(currentQuestion.id);

  return (
    <section className="rounded-xl border border-gray-200 p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-indigo-600">
            Assessment
          </p>

          <h2 className="mt-1 text-xl font-semibold">
            {assessment.title}
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            {lessonTitle}
          </p>
        </div>

        <span className="rounded-full bg-gray-100 px-3 py-1 text-sm">
          Question {currentQuestionIndex + 1} of {assessment.questions.length}
        </span>
      </div>

      {assessment.instructions && (
        <p className="mt-4 text-sm text-gray-600">
          {assessment.instructions}
        </p>
      )}

      <div className="mt-6">
        <p className="font-medium">{currentQuestion.question}</p>

        {currentQuestion.type === 'mcq' &&
          currentQuestion.options && (
            <div className="mt-4 space-y-3">
              {currentQuestion.options.map((option) => {
                const selected = currentAnswer === option.id;

                return (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => setAnswer(currentQuestion.id, option.id)}
                    className={`w-full rounded-lg border p-3 text-left transition ${
                      selected
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-400'
                    }`}
                  >
                    {option.text}
                  </button>
                );
              })}
            </div>
          )}

        {currentQuestion.type === 'subjective' && (
          <textarea
            value={typeof currentAnswer === 'string' ? currentAnswer : ''}
            onChange={(event) =>
              setAnswer(currentQuestion.id, event.target.value)
            }
            placeholder="Write your answer..."
            rows={5}
            className="mt-4 w-full rounded-lg border border-gray-300 p-3"
          />
        )}

        {currentQuestion.type === 'viva' && (
          <textarea
            value={typeof currentAnswer === 'string' ? currentAnswer : ''}
            onChange={(event) =>
              setAnswer(currentQuestion.id, event.target.value)
            }
            placeholder="Type your response..."
            rows={4}
            className="mt-4 w-full rounded-lg border border-gray-300 p-3"
          />
        )}

        {currentQuestion.type === 'case-study' && (
          <textarea
            value={typeof currentAnswer === 'string' ? currentAnswer : ''}
            onChange={(event) =>
              setAnswer(currentQuestion.id, event.target.value)
            }
            placeholder="Write your case-study analysis..."
            rows={6}
            className="mt-4 w-full rounded-lg border border-gray-300 p-3"
          />
        )}

        {currentQuestion.type === 'coding' && (
          <>
            {currentQuestion.code && (
              <pre className="mt-4 overflow-x-auto rounded-lg bg-gray-950 p-4 text-sm text-white">
                {currentQuestion.code}
              </pre>
            )}

            <p className="mt-3 text-xs text-gray-500">
              Language: {currentQuestion.language ?? 'Not specified'}
            </p>

            <textarea
              value={typeof currentAnswer === 'string' ? currentAnswer : ''}
              onChange={(event) =>
                setAnswer(currentQuestion.id, event.target.value)
              }
              placeholder="Write your code..."
              rows={8}
              className="mt-3 w-full rounded-lg border border-gray-300 p-3 font-mono text-sm"
            />
          </>
        )}
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-gray-500">
          Answered: {answeredCount}/{assessment.questions.length}
        </p>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={previousQuestion}
            disabled={currentQuestionIndex === 0 || isSubmitting}
            className="rounded-lg border px-4 py-2 disabled:opacity-40"
          >
            Previous
          </button>

          {!isLastQuestion ? (
            <button
              type="button"
              onClick={nextQuestion}
              disabled={isSubmitting}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-white disabled:opacity-40"
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting || answeredCount !== assessment.questions.length}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-white disabled:opacity-40"
            >
              {isSubmitting ? 'Submitting...' : 'Submit assessment'}
            </button>
          )}
        </div>
      </div>

      {(error || submitError) && (
        <p role="alert" className="mt-4 text-sm text-red-600">
          {submitError ?? error}
        </p>
      )}
    </section>
  );
}
