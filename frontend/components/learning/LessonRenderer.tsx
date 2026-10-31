
'use client';

import type { Lesson, LessonBlock } from '@/types/learning';

import TextBlock from './blocks/TextBlock';
import CodeBlock from './blocks/CodeBlock';
import QuestionBlock from './blocks/QuestionBlock';
import PracticeBlock from './blocks/PracticeBlock';
import VideoBlock from './blocks/VideoBlock';

import { Check, ChevronLeft, ChevronRight, Lock } from 'lucide-react';

interface LessonRendererProps {
  lesson: Lesson;
  completedBlockIds: string[];
  currentBlockIndex: number;
  isSaving: boolean;
  onMarkBlockComplete: (blockId: string) => Promise<void>;
  onPreviousBlock: () => void;
  onNextBlock: () => void;
}

function renderBlock(block: LessonBlock) {
  switch (block.type) {
    case 'TEXT':
      return <TextBlock block={block} />;
    case 'VIDEO':
      return <VideoBlock block={block} />;
    case 'CODE':
      return <CodeBlock block={block} />;
    case 'QUIZ':
      return <QuestionBlock block={block} />;
    case 'INTERACTIVE':
      return <PracticeBlock block={block} />;
    default:
      return (
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
          {block.title && (
            <h3 className="font-semibold text-[var(--text-primary)]">
              {block.title}
            </h3>
          )}
          {block.content && (
            <p className="mt-2 whitespace-pre-line text-sm leading-7 text-[var(--text-secondary)]">
              {block.content}
            </p>
          )}
          <p className="mt-3 text-xs text-[var(--text-muted)]">
            Unsupported block type: {block.type}
          </p>
        </section>
      );
  }
}

export default function LessonRenderer({
  lesson,
  completedBlockIds,
  currentBlockIndex,
  isSaving,
  onMarkBlockComplete,
  onPreviousBlock,
  onNextBlock,
}: LessonRendererProps) {
  const blocks = lesson.blocks;
  const total = blocks.length;
  const currentBlock = blocks[currentBlockIndex];

  if (!currentBlock || total === 0) {
    return (
      <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
        <p className="text-sm text-[var(--text-secondary)]">
          No lesson sections are available yet.
        </p>
      </section>
    );
  }

  const completedCount = blocks.filter((block) =>
    completedBlockIds.includes(block.id),
  ).length;

  const isCompleted = completedBlockIds.includes(currentBlock.id);
  const isLastBlock = currentBlockIndex === total - 1;
  const allCompleted = completedCount === total;

  return (
    <article className="mx-auto w-full max-w-4xl space-y-6">
      <header className="space-y-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--primary)]">
            Your learning session
          </p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-[var(--text-primary)] sm:text-3xl">
            {lesson.title}
          </h1>
          <p className="mt-2 text-sm leading-7 text-[var(--text-secondary)]">
            {lesson.objective}
          </p>
        </div>

        {lesson.prerequisites?.length ? (
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-alt)] p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-label)]">
              Before you begin
            </p>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
              {lesson.prerequisites.join(' · ')}
            </p>
          </div>
        ) : null}
      </header>

      {/* Overall progress */}
      <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 sm:p-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-[var(--text-primary)]">
              Your progress
            </p>
            <p className="mt-1 text-xs text-[var(--text-secondary)]">
              {completedCount} of {total} sections completed
            </p>
          </div>
          <span className="text-lg font-bold tabular-nums text-[var(--primary)]">
            {Math.round((completedCount / total) * 100)}%
          </span>
        </div>

        <div
          className="mt-4 h-2 overflow-hidden rounded-full bg-[var(--surface-alt)]"
          role="progressbar"
          aria-valuenow={completedCount}
          aria-valuemin={0}
          aria-valuemax={total}
          aria-label="Lesson completion"
        >
          <div
            className="h-full rounded-full bg-[var(--primary)] transition-all duration-500"
            style={{ width: `${(completedCount / total) * 100}%` }}
          />
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {blocks.map((block, index) => {
            const done = completedBlockIds.includes(block.id);
            const current = index === currentBlockIndex;
            const locked = index > currentBlockIndex && !done;

            return (
              <span
                key={block.id}
                title={`Section ${index + 1}${done ? ': completed' : current ? ': current' : ': locked'}`}
                className={`flex h-8 min-w-8 items-center justify-center rounded-full px-2 text-xs font-semibold ${
                  done
                    ? 'bg-emerald-500/10 text-emerald-700'
                    : current
                      ? 'bg-[var(--primary)] text-white'
                      : 'bg-[var(--surface-alt)] text-[var(--text-muted)]'
                }`}
              >
                {done ? <Check size={14} /> : locked ? <Lock size={12} /> : index + 1}
              </span>
            );
          })}
        </div>
      </section>

      {/* Current section */}
      <section
        key={currentBlock.id}
        className="rise space-y-5"
        aria-live="polite"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              Section {currentBlockIndex + 1} of {total}
            </p>
            <h2 className="mt-1 text-xl font-bold text-[var(--text-primary)]">
              {currentBlock.title || `Section ${currentBlockIndex + 1}`}
            </h2>
          </div>

          {isCompleted && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-700">
              <Check size={14} />
              Completed
            </span>
          )}
        </div>

        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-4 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-6">
          {renderBlock(currentBlock)}
        </div>

        <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
          <button
            type="button"
            onClick={onPreviousBlock}
            disabled={currentBlockIndex === 0 || isSaving}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-[var(--border)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)] disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft size={17} />
            Previous
          </button>

          {!isCompleted ? (
            <button
              type="button"
              disabled={isSaving}
              onClick={() => {
  void onMarkBlockComplete(currentBlock.id).catch(() => {
    // Error is handled by useLearning.
  });
}}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-wait disabled:opacity-60"
            >
              {isSaving ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Saving progress…
                </>
              ) : (
                <>
                  <Check size={17} />
                  Complete & continue
                  <ChevronRight size={17} />
                </>
              )}
            </button>
          ) : !isLastBlock ? (
            <button
              type="button"
              onClick={onNextBlock}
              disabled={isSaving}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:opacity-60"
            >
              Continue learning
              <ChevronRight size={17} />
            </button>
          ) : (
            <div className="rounded-xl bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-700">
              <Check className="mr-2 inline" size={16} />
              {allCompleted ? 'Lesson completed!' : 'Final section completed!'}
            </div>
          )}
        </div>
      </section>
    </article>
  );
}
