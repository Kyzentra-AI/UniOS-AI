
import type { Lesson, LessonBlock } from '@/types/learning';

import TextBlock from './blocks/TextBlock';
import CodeBlock from './blocks/CodeBlock';
import QuestionBlock from './blocks/QuestionBlock';
import PracticeBlock from './blocks/PracticeBlock';
import VideoBlock from './blocks/VideoBlock';

interface LessonRendererProps {
  lesson: Lesson;
  completedBlockIds: string[];
  onMarkBlockComplete: (blockId: string) => void;
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
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
          {block.title && (
            <h3 className="mb-2 font-semibold text-[var(--text-primary)]">
              {block.title}
            </h3>
          )}

          {block.content && (
            <p className="whitespace-pre-line text-sm leading-7 text-[var(--text-secondary)]">
              {block.content}
            </p>
          )}

          <p className="mt-3 text-xs text-[var(--text-muted)]">
            Unsupported lesson block type: {block.type}
          </p>
        </section>
      );
  }
}

export default function LessonRenderer({
  lesson,
  completedBlockIds,
  onMarkBlockComplete,
}: LessonRendererProps) {
  return (
    <article className="mx-auto w-full max-w-4xl space-y-8">
      <header className="space-y-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">
            {lesson.title}
          </h1>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            {lesson.objective}
          </p>
        </div>

        {lesson.prerequisites &&
          lesson.prerequisites.length > 0 && (
            <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-alt)] px-4 py-3">
              <span className="text-sm font-semibold text-[var(--text-label)]">
                Prerequisites
              </span>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                {lesson.prerequisites.join(', ')}
              </p>
            </div>
          )}
      </header>

      <div className="space-y-8">
        {lesson.blocks.map((block, index) => {
          const isCompleted = completedBlockIds.includes(block.id);

          return (
            <section key={block.id} className="space-y-3">
              <div className="flex items-center justify-between gap-3">
                <span className="text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
                  Section {index + 1} of {lesson.blocks.length}
                </span>

                <button
                  type="button"
                  disabled={isCompleted}
                  onClick={() => onMarkBlockComplete(block.id)}
                  className={`rounded-lg px-3 py-2 text-xs font-semibold transition ${
                    isCompleted
                      ? 'cursor-default bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
                      : 'border border-[var(--border)] bg-[var(--surface)] text-[var(--text-primary)] hover:bg-[var(--surface-alt)]'
                  }`}
                >
                  {isCompleted ? '✓ Completed' : 'Mark complete'}
                </button>
              </div>

              {renderBlock(block)}
            </section>
          );
        })}
      </div>
    </article>
  );
}
