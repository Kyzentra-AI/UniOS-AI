
import type { ReactNode } from 'react';
import type { LessonBlock } from '@/types/learning';

interface TextBlockProps {
  block: LessonBlock;
}

function renderInline(text: string): ReactNode[] {
  const pattern = /(\*\*[^*]+\*\*|__[^_]+__|`[^`]+`|\*[^*]+\*)/g;
  const parts = text.split(pattern);

  return parts.map((part, index) => {
    if (
      (part.startsWith('**') && part.endsWith('**')) ||
      (part.startsWith('__') && part.endsWith('__'))
    ) {
      return (
        <strong
          key={index}
          className="font-semibold text-[var(--text-primary)]"
        >
          {part.slice(2, -2)}
        </strong>
      );
    }

    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code
          key={index}
          className="rounded-md bg-[var(--surface-alt)] px-1.5 py-0.5 font-mono text-[0.9em] text-[var(--primary)]"
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={index}>{part.slice(1, -1)}</em>;
    }

    return part;
  });
}

export default function TextBlock({ block }: TextBlockProps) {
  const lines = (block.content ?? '').replace(/\r\n/g, '\n').split('\n');

  const elements: ReactNode[] = [];
  let bulletItems: string[] = [];
  let numberedItems: string[] = [];

  const flushLists = () => {
    if (bulletItems.length) {
      elements.push(
        <ul
          key={`ul-${elements.length}`}
          className="my-4 space-y-2 pl-5 text-sm leading-7 text-[var(--text-secondary)] marker:text-[var(--primary)]"
        >
          {bulletItems.map((item, index) => (
            <li key={index} className="list-disc pl-1">
              {renderInline(item)}
            </li>
          ))}
        </ul>,
      );
      bulletItems = [];
    }

    if (numberedItems.length) {
      elements.push(
        <ol
          key={`ol-${elements.length}`}
          className="my-4 space-y-2 pl-5 text-sm leading-7 text-[var(--text-secondary)] marker:font-semibold marker:text-[var(--primary)]"
        >
          {numberedItems.map((item, index) => (
            <li key={index} className="list-decimal pl-1">
              {renderInline(item)}
            </li>
          ))}
        </ol>,
      );
      numberedItems = [];
    }
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    if (!trimmed) {
      flushLists();
      return;
    }

    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);

    if (heading) {
      flushLists();

      const level = heading[1].length;
      const content = renderInline(heading[2]);
      const className =
        level === 1
          ? 'mt-6 text-xl font-bold text-[var(--text-primary)]'
          : level === 2
            ? 'mt-5 text-lg font-semibold text-[var(--text-primary)]'
            : 'mt-4 text-base font-semibold text-[var(--text-primary)]';

      elements.push(
        level === 1 ? (
          <h2 key={index} className={className}>{content}</h2>
        ) : level === 2 ? (
          <h3 key={index} className={className}>{content}</h3>
        ) : (
          <h4 key={index} className={className}>{content}</h4>
        ),
      );
      return;
    }

    const bullet = trimmed.match(/^[-*•]\s+(.+)$/);

    if (bullet) {
      numberedItems.length && flushLists();
      bulletItems.push(bullet[1]);
      return;
    }

    const numbered = trimmed.match(/^\d+[.)]\s+(.+)$/);

    if (numbered) {
      bulletItems.length && flushLists();
      numberedItems.push(numbered[1]);
      return;
    }

    flushLists();

    elements.push(
      <p
        key={index}
        className="text-sm leading-7 text-[var(--text-secondary)]"
      >
        {renderInline(trimmed)}
      </p>,
    );
  });

  flushLists();

  return (
    <div className="space-y-3">
      {elements.length > 0 ? (
        elements
      ) : (
        <p className="text-sm leading-7 text-[var(--text-muted)]">
          No lesson content is available for this section.
        </p>
      )}
    </div>
  );
}
