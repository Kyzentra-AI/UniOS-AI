
import type { LessonBlock } from '@/types/learning';
import DiagramBlock from './DiagramBlock';
import MarkdownContent from './MarkdownContent';

interface TextBlockProps {
  block: LessonBlock;
}

export default function TextBlock({ block }: TextBlockProps) {
  if (block.content?.includes('Renderer Type: Diagram')) {
    return <DiagramBlock block={block} />;
  }

  return (
    <section className="space-y-3">
      {block.title && (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      <MarkdownContent content={block.content ?? ''} />
    </section>
  );
}
