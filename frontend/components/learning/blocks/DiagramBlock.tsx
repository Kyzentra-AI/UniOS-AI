
"use client";

import { useState } from "react";
import type { LessonBlock } from "@/types/learning";
import {
  Workflow,
  ArrowDown,
  Layers,
  Copy,
  Check,
} from "lucide-react";

import MermaidDiagram from "./MermaidDiagram";

interface DiagramBlockProps {
  block: LessonBlock;
}

interface ParsedStep {
  step: number;
  title: string;
  detail?: string;
}

function cleanDiagramContent(content: string): string {
  return content
    .replace(
      /^\s*Renderer\s*Type\s*:\s*Diagram\s*\.?\s*/i,
      "",
    )
    .trim();
}

function removeCodeFence(content: string): string {
  return content
    .replace(/^\s*```[^\n]*\n?/, "")
    .replace(/\n?```\s*$/, "")
    .trim();
}

function isMermaid(content: string): boolean {
  const cleaned = cleanDiagramContent(content);
  const withoutFence = removeCodeFence(cleaned);
  const trimmed = withoutFence.trim();

  if (/^\s*```mermaid\b/i.test(cleaned)) {
    return true;
  }

  return /^(?:flowchart|graph|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|gantt|pie|journey|gitGraph|mindmap|timeline|quadrantChart|requirementDiagram|C4Context|sankey-beta)\b/i.test(
    trimmed,
  );
}

function isAsciiArt(content: string): boolean {
  return (
    content.includes("+--") ||
    content.includes("+==") ||
    content.includes("|  ") ||
    content.includes("│") ||
    content.includes("┌") ||
    content.includes("└") ||
    content.includes("├") ||
    content.includes("┬") ||
    content.includes("┴") ||
    content.includes("┐") ||
    content.includes("┘") ||
    content.includes("-->") ||
    content.includes("<--") ||
    content.includes("==>") ||
    content.includes("<-")
  );
}

function parseDiagramSteps(content: string): ParsedStep[] {
  const cleaned = cleanDiagramContent(content);

  const lines = cleaned.split(/\r?\n/);
  const parsed: Array<{ step: number; body: string }> = [];

  let currentStep: { step: number; body: string } | null = null;

  const stepPattern =
    /^\s*(?:Step\s+)?(\d+)\s*(?:[.):\-]\s*|\s+)(.+?)\s*$/i;

  for (const line of lines) {
    const match = line.match(stepPattern);

    if (match) {
      if (currentStep) {
        parsed.push(currentStep);
      }

      currentStep = {
        step: Number(match[1]),
        body: match[2].trim(),
      };

      continue;
    }

    if (currentStep && line.trim()) {
      currentStep.body += ` ${line.trim()}`;
    }
  }

  if (currentStep) {
    parsed.push(currentStep);
  }

  return parsed
    .filter((item) => item.body.length > 0)
    .map((item) => {
      const body = item.body;
      const firstSentenceEnd = body.search(/[.!?](?:\s|$)/);

      let title = body;
      let detail: string | undefined;

      if (firstSentenceEnd !== -1 && firstSentenceEnd < body.length - 1) {
        title = body.slice(0, firstSentenceEnd + 1).trim();
        detail = body.slice(firstSentenceEnd + 1).trim();
      }

      return {
        step: item.step,
        title,
        detail: detail || undefined,
      };
    });
}

export default function DiagramBlock({
  block,
}: DiagramBlockProps) {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);

  const rawContent = (
    block.content ??
    block.code ??
    ""
  ).trim();

  const cleanedContent = cleanDiagramContent(rawContent);
  const mermaidDiagram = isMermaid(rawContent);
  const diagramSource = removeCodeFence(cleanedContent);

  const handleCopy = async () => {
    if (!rawContent) return;

    try {
      await navigator.clipboard.writeText(rawContent);

      setCopied(true);
      setCopyError(false);

      window.setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch {
      setCopyError(true);
      setCopied(false);
    }
  };

  // Case 1: Image URL diagram
  if (block.url) {
    return (
      <section className="space-y-3">
        {block.title && (
          <h3 className="text-base font-semibold text-[var(--text-primary)]">
            {block.title}
          </h3>
        )}

        <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-2 shadow-sm">
          <img
            src={block.url}
            alt={block.caption ?? block.title ?? "Lesson diagram"}
            className="max-h-[520px] w-full rounded-xl object-contain"
          />

          {block.caption && (
            <p className="mt-2 text-center text-xs text-[var(--text-muted)]">
              {block.caption}
            </p>
          )}
        </div>
      </section>
    );
  }

  // Case 2: Mermaid diagram
  if (rawContent && mermaidDiagram) {
    return (
      <section className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-2">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[var(--primary)]/10 text-[var(--primary)]">
              <Workflow className="h-4 w-4" />
            </div>

            <h3 className="truncate text-base font-semibold text-[var(--text-primary)]">
              {block.title ?? "Architecture Flow"}
            </h3>
          </div>

          <button
            type="button"
            onClick={() => void handleCopy()}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1 text-xs font-medium text-[var(--text-secondary)] transition hover:bg-[var(--surface-alt)]"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-500" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        {copyError && (
          <p className="text-xs text-red-500">
            Unable to copy diagram source.
          </p>
        )}

        <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface-alt)] p-2 shadow-sm">
          <div className="border-b border-[var(--border)] px-3 py-2 text-xs font-mono text-[var(--text-muted)]">
            mermaid-diagram
          </div>

          <div className="p-2">
            <MermaidDiagram chart={diagramSource} />
          </div>
        </div>
      </section>
    );
  }

  // Case 3: ASCII or other preformatted diagram
  if (
    rawContent &&
    (isAsciiArt(cleanedContent) || rawContent.includes("```"))
  ) {
    const displayCode = removeCodeFence(cleanedContent);

    return (
      <section className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-2">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[var(--primary)]/10 text-[var(--primary)]">
              <Workflow className="h-4 w-4" />
            </div>

            <h3 className="truncate text-base font-semibold text-[var(--text-primary)]">
              {block.title ?? "Architecture Diagram (ASCII)"}
            </h3>
          </div>

          <button
            type="button"
            onClick={() => void handleCopy()}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1 text-xs font-medium text-[var(--text-secondary)] transition hover:bg-[var(--surface-alt)]"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-500" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        {copyError && (
          <p className="text-xs text-red-500">
            Unable to copy diagram source.
          </p>
        )}

        <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface-alt)] shadow-sm">
          <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-2 text-xs font-mono text-[var(--text-muted)]">
            <span>ascii-diagram</span>
            <span>visual-schema</span>
          </div>

          <pre className="overflow-x-auto whitespace-pre p-4 font-mono text-xs leading-relaxed text-[var(--text-primary)] sm:text-sm">
            <code>{displayCode}</code>
          </pre>
        </div>
      </section>
    );
  }

  // Case 4: Step-by-step diagram instructions
  const parsedSteps = rawContent
    ? parseDiagramSteps(rawContent)
    : [];

  if (parsedSteps.length > 0) {
    return (
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--primary)]/10 text-[var(--primary)]">
              <Layers className="h-4 w-4" />
            </div>

            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              {block.title ?? "Process Flow & Architecture"}
            </h3>
          </div>

          <span className="rounded-full bg-[var(--surface-alt)] px-2.5 py-0.5 text-xs font-medium text-[var(--text-muted)]">
            {parsedSteps.length} Steps
          </span>
        </div>

        <div className="space-y-3 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-wider text-[var(--primary)]">
            Visual Execution Sequence
          </p>

          <div className="flex flex-col items-center gap-2 pt-2">
            {parsedSteps.map((step, index) => (
              <div
                key={`${step.step}-${index}`}
                className="flex w-full flex-col items-center"
              >
                <div className="w-full max-w-xl rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4 transition hover:border-[var(--primary)]/50">
                  <div className="flex items-start gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--primary)] text-xs font-bold text-white shadow-sm">
                      {step.step}
                    </span>

                    <div className="space-y-1">
                      <p className="text-sm font-medium text-[var(--text-primary)]">
                        {step.title}
                      </p>

                      {step.detail && (
                        <p className="text-xs leading-relaxed text-[var(--text-secondary)]">
                          {step.detail}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {index < parsedSteps.length - 1 && (
                  <div className="py-1 text-[var(--text-muted)]">
                    <ArrowDown className="h-4 w-4 animate-bounce" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  // Case 5: General text fallback
  return (
    <section className="space-y-3">
      {block.title && (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      {rawContent ? (
        <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface-alt)] p-5 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            <Workflow className="h-4 w-4 text-[var(--primary)]" />

            <span className="text-xs font-semibold uppercase tracking-wider text-[var(--primary)]">
              Diagram Overview
            </span>
          </div>

          <p className="whitespace-pre-line text-sm leading-relaxed text-[var(--text-primary)]">
            {cleanedContent}
          </p>
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface-alt)] p-8 text-center text-sm text-[var(--text-muted)]">
          Diagram content will appear here.
        </div>
      )}
    </section>
  );
}
