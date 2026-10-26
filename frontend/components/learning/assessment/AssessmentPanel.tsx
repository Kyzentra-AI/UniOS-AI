
'use client';

import { useEffect, useState } from 'react';

import type { Lesson } from '@/types/learning';
import type { Assessment } from '@/types/assessment';

import { useAssessment } from '@/hooks/useAssessment';
import { Check, Chevron, stagger } from '@/components/roadmap/UI';

interface AssessmentPanelProps {
  lesson: Lesson;
  assessment?: Assessment | null;
  topic: string;
  sessionId?: string;
  isLoading?: boolean;
  loadError?: string | null;
  onRetry?: () => void;
}

const card =
  'rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-7';

const answerField =
  'mt-4 w-full rounded-2xl border border-[var(--border)] bg-[var(--background)] p-4 text-sm leading-6 text-[var(--text-primary)] outline-none transition placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:shadow-[0_0_0_4px_var(--primary-soft)]';

export default function AssessmentPanel({
  lesson,
  assessment,
  topic,
  sessionId,
  isLoading = false,
  loadError = null,
  onRetry,
}: AssessmentPanelProps) {
  if (isLoading) {
    return (
      <section className={`rise ${card}`} role="status" aria-live="polite">
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Preparing your assessment…
        </h2>

        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          Generating questions for {lesson.title}.
        </p>

        <div className="mt-6 space-y-3" aria-hidden="true">
          <div className="skeleton h-4 w-2/3 rounded-md" />
          <div className="skeleton h-12 w-full rounded-xl" />
          <div className="skeleton h-12 w-full rounded-xl" />
          <div className="skeleton h-12 w-5/6 rounded-xl" />
        </div>
      </section>
    );
  }

  if (loadError) {
    return (
      <section className={`rise ${card}`} role="alert">
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Unable to load assessment
        </h2>

        <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
          {loadError}
        </p>

        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-5 rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
          >
            Try again
          </button>
        )}
      </section>
    );
  }

  if (!assessment || assessment.questions.length === 0) {
    return (
      <section className={`rise ${card}`}>
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Check your understanding
        </h2>

        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          Assessment for {lesson.title}
        </p>

        <div className="mt-6 rounded-2xl border border-dashed border-[var(--border)] bg-[var(--background)] px-5 py-8 text-center">
          <div
            aria-hidden="true"
            className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-full border-2 border-dashed border-[var(--primary)] bg-[var(--primary-soft)]"
          >
            <span className="h-2.5 w-2.5 rounded-full bg-[var(--primary)]" />
          </div>

          <p className="text-sm text-[var(--text-secondary)]">
            No assessment questions are available yet.
          </p>

          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="mt-4 rounded-xl border border-[var(--border)] px-4 py-2 text-sm font-semibold text-[var(--text-primary)] transition hover:border-[var(--primary)]"
            >
              Generate assessment
            </button>
          )}
        </div>
      </section>
    );
  }

  return (
    <AssessmentForm
      key={assessment.id}
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

  const isAnswered = (questionId: string) => {
    const answer = getAnswer(questionId);

    if (Array.isArray(answer)) return answer.length > 0;

    if (typeof answer === 'object' && answer !== null) {
      return Object.keys(answer).length > 0;
    }

    return String(answer).trim().length > 0;
  };

  const answeredCount = assessment.questions.filter((question) =>
    isAnswered(question.id),
  ).length;

  async function handleSubmit() {
    setSubmitError(null);

    try {
      await submit();
    } catch {
      setSubmitError(
        'Your assessment could not be submitted. Please try again.',
      );
    }
  }

  if (result) {
    return (
      <section className={`rise ${card}`}>
        <h2 className="text-xl font-semibold text-[var(--text-primary)]">
          Assessment results
        </h2>

        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          {lessonTitle}
        </p>

        {result.score != null && (
          <div className="pop mt-6 inline-flex items-baseline gap-2 rounded-2xl bg-[var(--primary-soft)] px-5 py-4">
            <span className="text-sm text-[var(--text-secondary)]">
              Score
            </span>

            <span className="text-4xl font-bold tracking-tight text-[var(--primary)]">
              {result.score}
            </span>
          </div>
        )}

        <p className="mt-5 max-w-2xl text-[15px] leading-7 text-[var(--text-primary)]">
          {result.feedback ?? 'Your assessment has been submitted.'}
        </p>

        {result.mastery_updates && (
          <details className="group mt-6 rounded-2xl border border-[var(--border)]">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3 text-sm font-medium text-[var(--text-primary)] [&::-webkit-details-marker]:hidden">
              Mastery updates
              <Chevron className="rotate-90 text-[var(--text-muted)] transition-transform duration-200 group-open:-rotate-90" />
            </summary>

            <pre className="overflow-x-auto border-t border-[var(--border)] bg-[var(--background)] p-4 text-xs leading-5 text-[var(--text-secondary)]">
              {JSON.stringify(result.mastery_updates, null, 2)}
            </pre>
          </details>
        )}
      </section>
    );
  }

  if (!currentQuestion) return null;

  const currentAnswer = getAnswer(currentQuestion.id);
  const total = assessment.questions.length;

  return (
    <section className={`rise ${card}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-[var(--primary)]">
            Assessment
          </p>

          <h2 className="mt-1 text-xl font-semibold text-[var(--text-primary)]">
            {assessment.title}
          </h2>

          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            {lessonTitle}
          </p>
        </div>

        <span className="shrink-0 rounded-full border border-[var(--border)] bg-[var(--surface-alt)] px-3 py-1 text-sm font-medium text-[var(--text-secondary)]">
          Question {currentQuestionIndex + 1} of {total}
        </span>
      </div>

      <div
        className="mt-5 flex gap-[3px]"
        role="img"
        aria-label={`${answeredCount} of ${total} questions answered`}
      >
        {assessment.questions.map((question, index) => (
          <span
            key={question.id}
            className="seg h-1.5 flex-1 rounded-full transition-colors duration-300"
            style={{
              ...stagger(Math.min(index, 40)),
              backgroundColor: isAnswered(question.id)
                ? 'var(--primary)'
                : index === currentQuestionIndex
                  ? 'var(--text-muted)'
                  : 'var(--border)',
            }}
          />
        ))}
      </div>

      {assessment.instructions && (
        <p className="mt-5 rounded-2xl bg-[var(--surface-alt)] px-4 py-3 text-sm leading-6 text-[var(--text-secondary)]">
          {assessment.instructions}
        </p>
      )}

      <div key={currentQuestion.id} className="rise mt-7">
        <p className="text-lg font-semibold leading-snug text-[var(--text-primary)]">
          {currentQuestion.question}
        </p>

        {currentQuestion.type === 'mcq' &&
          currentQuestion.options && (
            <div
              className="mt-5 space-y-2.5"
              role="radiogroup"
              aria-label="Answer options"
            >
              {currentQuestion.options.map((option, index) => {
                const selected = currentAnswer === option.id;

                return (
                  <button
                    key={option.id}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    onClick={() =>
                      setAnswer(currentQuestion.id, option.id)
                    }
                    className={`group flex w-full items-center gap-3.5 rounded-2xl border p-3.5 text-left transition duration-200 active:scale-[0.995] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)]'
                        : 'border-[var(--border)] hover:-translate-y-px hover:border-[var(--primary)] hover:shadow-[0_6px_18px_rgba(24,52,58,0.06)]'
                    }`}
                  >
                    <span
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold transition-colors duration-200 ${
                        selected
                          ? 'border-[var(--primary)] bg-[var(--primary)] text-white'
                          : 'border-[var(--border)] text-[var(--text-muted)] group-hover:border-[var(--primary)]'
                      }`}
                    >
                      {selected ? (
                        <Check />
                      ) : (
                        String.fromCharCode(65 + index)
                      )}
                    </span>

                    <span className="min-w-0 text-[15px] leading-6 text-[var(--text-primary)]">
                      {option.text}
                    </span>
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
            className={answerField}
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
            className={answerField}
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
            className={answerField}
          />
        )}

        {currentQuestion.type === 'coding' && (
          <>
            {currentQuestion.code && (
              <pre className="mt-5 overflow-x-auto rounded-2xl bg-gray-950 p-4 text-sm leading-6 text-white">
                {currentQuestion.code}
              </pre>
            )}

            <p className="mt-3 text-xs text-[var(--text-secondary)]">
              Language: {currentQuestion.language ?? 'Not specified'}
            </p>

            <textarea
              value={typeof currentAnswer === 'string' ? currentAnswer : ''}
              onChange={(event) =>
                setAnswer(currentQuestion.id, event.target.value)
              }
              placeholder="Write your code..."
              rows={8}
              spellCheck={false}
              className={`${answerField} !mt-3 font-mono`}
            />
          </>
        )}
      </div>

      <div className="mt-8 flex flex-col gap-4 border-t border-[var(--border)] pt-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-[var(--text-secondary)]">
            Answered: {answeredCount}/{total}
          </p>

          {isLastQuestion && answeredCount !== total && (
            <p className="rise mt-0.5 text-xs text-[var(--text-muted)]">
              Answer every question to submit.
            </p>
          )}
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={previousQuestion}
            disabled={currentQuestionIndex === 0 || isSubmitting}
            className="flex-1 rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition hover:border-[var(--primary)] active:scale-[0.98] disabled:opacity-40 disabled:hover:border-[var(--border)] sm:flex-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
          >
            Previous
          </button>

          {!isLastQuestion ? (
            <button
              type="button"
              onClick={nextQuestion}
              disabled={isSubmitting}
              className="group inline-flex flex-1 items-center justify-center gap-1 rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] active:scale-[0.98] disabled:opacity-40 sm:flex-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
            >
              Next
              <Chevron className="transition-transform duration-200 group-hover:translate-x-0.5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={
                isSubmitting ||
                answeredCount !== assessment.questions.length
              }
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] active:scale-[0.98] disabled:opacity-40 sm:flex-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
            >
              {isSubmitting && (
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
              )}
              {isSubmitting ? 'Submitting...' : 'Submit assessment'}
            </button>
          )}
        </div>
      </div>

      {(error || submitError) && (
        <p
          role="alert"
          className="rise mt-4 flex items-start gap-2.5 rounded-2xl border border-red-500/30 bg-red-500/5 p-3.5 text-sm text-red-600"
        >
          <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-red-500" />
          {submitError ?? error}
        </p>
      )}
    </section>
  );
}
