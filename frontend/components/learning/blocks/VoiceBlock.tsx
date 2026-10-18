import type { LessonBlock } from '@/types/learning';

interface VoiceBlockProps {
  block: LessonBlock;
}

export default function VoiceBlock({
  block,
}: VoiceBlockProps) {
  return (
    <section className="space-y-3">
      {block.title && (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      {block.url ? (
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
          <audio
            controls
            className="w-full"
            src={block.url}
          >
            Your browser does not support audio playback.
          </audio>
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-alt)] p-6 text-center text-sm text-[var(--text-muted)]">
          Voice content will appear here.
        </div>
      )}
    </section>
  );
}