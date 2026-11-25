
import type { LessonBlock } from "@/types/learning";
import MarkdownContent from "./MarkdownContent";

interface CodeBlockProps {
  block: LessonBlock;
}

function createMarkdownFence(code: string): string {
  const matches = code.match(/`{3,}/g) ?? [];

  const longestFence = Math.max(
    2,
    ...matches.map((fence) => fence.length),
  );

  return "`".repeat(longestFence + 1);
}

export default function CodeBlock({
  block,
}: CodeBlockProps) {
  const code = block.code ?? block.content ?? "";
  const language = (block.language ?? "text")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_+-]/g, "");

  const fence = createMarkdownFence(code);
  const markdown = `${fence}${language}\n${code}\n${fence}`;

  return (
    <section className="space-y-3">
      {block.title && (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--primary)]">
        {block.language && (
          <div className="border-b border-white/10 px-4 py-2 text-xs text-white/70">
            {block.language}
          </div>
        )}

        <div className="[&_.hljs]:!bg-transparent [&_pre]:!my-0 [&_pre]:!border-0 [&_pre]:!bg-transparent [&_pre]:!p-5 [&_pre]:text-sm [&_pre]:leading-6 [&_pre]:text-white">
          <MarkdownContent content={markdown} />
        </div>
      </div>
    </section>
  );
}
