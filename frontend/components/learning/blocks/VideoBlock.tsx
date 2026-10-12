import type { LessonBlock } from '@/types/learning';

interface VideoBlockProps {
  block: LessonBlock;
}

export default function VideoBlock({
  block,
}: VideoBlockProps) {
  return (
    <section className="space-y-3">
      {block.title && (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      {block.url ? (
        <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--primary)]">
          <video
            controls
            className="w-full"
            src={block.url}
          >
            Your browser does not support video playback.
          </video>
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-alt)] p-8 text-center text-sm text-[var(--text-muted)]">
          Video content will appear here.
        </div>
      )}
    </section>
  );
}