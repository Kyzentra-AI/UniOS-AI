import type {
  Lesson,
  LessonBlock,
} from '@/types/learning';

import TextBlock from './blocks/TextBlock';
import CodeBlock from './blocks/CodeBlock';
import QuestionBlock from './blocks/QuestionBlock';
import PracticeBlock from './blocks/PracticeBlock';
import VideoBlock from './blocks/VideoBlock';

interface LessonRendererProps {
  lesson: Lesson;
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
        {lesson.blocks.map((block) => (
          <div key={block.id}>
            {renderBlock(block)}
          </div>
        ))}
      </div>
    </article>
  );
}
