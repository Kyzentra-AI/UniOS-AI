'use client';

import { useState } from 'react';

export interface AssessmentQuestion {
  question_id: string;
  text: string;
  type: string;
  options: string[];
}

export type AssessmentAnswer = string | string[];

export interface AssessmentProps {
  questions: AssessmentQuestion[];
  onSubmit: (
    answers: Record<string, AssessmentAnswer>
  ) => void | Promise<void>;
  isSubmitting?: boolean;
}

export default function Assessment({
  questions,
  onSubmit,
  isSubmitting = false,
}: AssessmentProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<
    Record<string, AssessmentAnswer>
  >({});

  if (questions.length === 0) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <p className="text-sm text-neutral-500">
          No questions available.
        </p>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];

  const selectedAnswer =
    answers[currentQuestion.question_id];

  const isLastQuestion =
    currentIndex === questions.length - 1;

  const questionType =
    currentQuestion.type.toLowerCase();

  const isTextQuestion =
    questionType === 'text';

  const isMultiSelect =
    questionType === 'multi_select';

  const isSingleSelect =
    questionType === 'single_select' ||
    questionType === 'choice';

  const hasAnswer =
    typeof selectedAnswer === 'string'
      ? selectedAnswer.trim().length > 0
      : Array.isArray(selectedAnswer)
        ? selectedAnswer.length > 0
        : false;

  const handleSingleSelect = (option: string) => {
    setAnswers((previous) => ({
      ...previous,
      [currentQuestion.question_id]: option,
    }));
  };

  const handleMultiSelect = (option: string) => {
    setAnswers((previous) => {
      const current =
        previous[currentQuestion.question_id];

      const selected = Array.isArray(current)
        ? current
        : [];

      const alreadySelected =
        selected.includes(option);

      const updated = alreadySelected
        ? selected.filter((item) => item !== option)
        : [...selected, option];

      return {
        ...previous,
        [currentQuestion.question_id]: updated,
      };
    });
  };

  const handleTextChange = (value: string) => {
    setAnswers((previous) => ({
      ...previous,
      [currentQuestion.question_id]: value,
    }));
  };

  const handleNext = () => {
    if (!hasAnswer || isSubmitting) {
      return;
    }

    if (isLastQuestion) {
      void onSubmit(answers);
      return;
    }

    setCurrentIndex((previous) => previous + 1);
  };

  const handlePrevious = () => {
    if (currentIndex === 0 || isSubmitting) {
      return;
    }

    setCurrentIndex((previous) => previous - 1);
  };

  const progress =
    ((currentIndex + 1) / questions.length) * 100;

  const selectedOptions = Array.isArray(selectedAnswer)
    ? selectedAnswer
    : [];

  return (
    <div className="mx-auto w-full max-w-3xl">
      <div className="mb-8">
        <p className="mb-2 text-sm font-medium text-neutral-500">
          Getting to know you
        </p>

        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-neutral-900">
            A few questions about you
          </h1>

          <span className="text-sm text-neutral-500">
            {currentIndex + 1} / {questions.length}
          </span>
        </div>

        <div className="h-1.5 w-full overflow-hidden rounded-full bg-neutral-200">
          <div
            className="h-full rounded-full bg-neutral-900 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="rounded-2xl border border-neutral-200 bg-white p-6 shadow-sm">
        <h2 className="mb-6 text-lg font-medium leading-7 text-neutral-900">
          {currentQuestion.text}
        </h2>

        {isTextQuestion && (
          <textarea
            value={
              typeof selectedAnswer === 'string'
                ? selectedAnswer
                : ''
            }
            onChange={(event) =>
              handleTextChange(event.target.value)
            }
            placeholder="Type your answer..."
            disabled={isSubmitting}
            rows={5}
            className="w-full resize-none rounded-xl border border-neutral-300 px-4 py-3 text-sm outline-none transition focus:border-neutral-900 focus:ring-1 focus:ring-neutral-900 disabled:cursor-not-allowed disabled:bg-neutral-100"
          />
        )}

        {(isSingleSelect || isMultiSelect) && (
          <div className="space-y-3">
            {currentQuestion.options.map((option) => {
              const isSelected = isMultiSelect
                ? selectedOptions.includes(option)
                : selectedAnswer === option;

              return (
                <button
                  key={option}
                  type="button"
                  onClick={() =>
                    isMultiSelect
                      ? handleMultiSelect(option)
                      : handleSingleSelect(option)
                  }
                  disabled={isSubmitting}
                  className={`w-full rounded-xl border px-4 py-3 text-left text-sm transition ${
                    isSelected
                      ? 'border-neutral-900 bg-neutral-900 text-white'
                      : 'border-neutral-200 bg-white text-neutral-800 hover:border-neutral-400'
                  } disabled:cursor-not-allowed disabled:opacity-60`}
                >
                  {option}
                </button>
              );
            })}
          </div>
        )}

        {!isTextQuestion &&
          !isSingleSelect &&
          !isMultiSelect && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              This question type is not supported yet.
            </div>
          )}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <button
          type="button"
          onClick={handlePrevious}
          disabled={currentIndex === 0 || isSubmitting}
          className="rounded-xl border border-neutral-200 px-5 py-2.5 text-sm font-medium text-neutral-700 transition hover:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Back
        </button>

        <button
          type="button"
          onClick={handleNext}
          disabled={!hasAnswer || isSubmitting}
          className="rounded-xl bg-neutral-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isSubmitting
            ? 'Submitting...'
            : isLastQuestion
              ? 'Submit'
              : 'Next'}
        </button>
      </div>
    </div>
  );
}