'use client';

import { useState } from 'react';
import type { LessonBlock } from '@/types/learning';
import { Workflow, ArrowDown, Layers, Copy, Check } from 'lucide-react';

interface DiagramBlockProps {
  block: LessonBlock;
}

interface ParsedStep {
  step: number;
  title: string;
  detail?: string;
}

function parseDiagramSteps(content: string): ParsedStep[] {
  // Clean off "Renderer Type: Diagram." prefix if present
  const cleaned = content.replace(/^Renderer\s*Type:\s*Diagram\.?\s*/i, '').trim();

  const steps: ParsedStep[] = [];
  // Match "Step 1: ...", "Step 1 - ...", or "1. Draw ..."
  const stepRegex = /(?:Step\s*(\d+)[:.-]?\s*|(\d+)\.\s*)([^\n]+(?:\n(?!(?:Step\s*\d+|\d+\.))[^\n]+)*)/gi;
  let match: RegExpExecArray | null;

  while ((match = stepRegex.exec(cleaned)) !== null) {
    const num = parseInt(match[1] || match[2], 10);
    const body = (match[3] || '').trim();

    if (body) {
      // Split first sentence/clause as title, remainder as detail
      const firstSentenceEnd = body.search(/[.!?](?:\s|$)/);
      let title = body;
      let detail: string | undefined;

      if (firstSentenceEnd !== -1 && firstSentenceEnd < body.length - 2) {
        title = body.slice(0, firstSentenceEnd + 1).trim();
        detail = body.slice(firstSentenceEnd + 1).trim();
      }

      steps.push({
        step: num,
        title,
        detail: detail || undefined,
      });
    }
  }

  return steps;
}

function isAsciiArt(text: string): boolean {
  return (
    text.includes('+--') ||
    text.includes('+==') ||
    text.includes('|  ') ||
    text.includes('│') ||
    text.includes('┌') ||
    text.includes('└') ||
    text.includes('-->') ||
    text.includes('==>') ||
    text.includes('<-')
  );
}

function isMermaid(text: string): boolean {
  const t = text.trim();
  return (
    t.startsWith('```mermaid') ||
    t.startsWith('flowchart ') ||
    t.startsWith('graph ') ||
    t.startsWith('sequenceDiagram') ||
    t.startsWith('classDiagram') ||
    t.startsWith('stateDiagram')
  );
}

export default function DiagramBlock({ block }: DiagramBlockProps) {
  const [copied, setCopied] = useState(false);
  const rawContent = (block.content ?? block.code ?? '').trim();

  const handleCopy = () => {
    if (!rawContent) return;
    navigator.clipboard.writeText(rawContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Case 1: Image URL Diagram
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
            alt={block.caption ?? block.title ?? 'Lesson diagram'}
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

  // Case 2: ASCII or Mermaid preformatted block
  if (rawContent && (isAsciiArt(rawContent) || isMermaid(rawContent) || rawContent.includes('```'))) {
    // Strip markdown code fences if wrapped
    const displayCode = rawContent.replace(/^```[a-z]*\n?/i, '').replace(/\n?```$/i, '');
    const isMermaidSyntax = isMermaid(rawContent);

    return (
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--primary)]/10 text-[var(--primary)]">
              <Workflow className="h-4 w-4" />
            </div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              {block.title ?? (isMermaidSyntax ? 'Architecture Flow (Mermaid)' : 'Architecture Diagram (ASCII)')}
            </h3>
          </div>

          <button
            type="button"
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1 text-xs font-medium text-[var(--text-secondary)] transition hover:bg-[var(--surface-alt)]"
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

        <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface-alt)] shadow-sm">
          <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-2 text-xs font-mono text-[var(--text-muted)]">
            <span>{isMermaidSyntax ? 'mermaid-diagram' : 'ascii-diagram'}</span>
            <span>visual-schema</span>
          </div>
          <pre className="overflow-x-auto p-4 font-mono text-xs sm:text-sm leading-relaxed text-[var(--text-primary)]">
            <code>{displayCode}</code>
          </pre>
        </div>
      </section>
    );
  }

  // Case 3: Step-by-Step Diagram Instructions (e.g. "Renderer Type: Diagram. Step 1: Draw a rectangle...")
  const parsedSteps = rawContent ? parseDiagramSteps(rawContent) : [];

  if (parsedSteps.length > 0) {
    return (
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--primary)]/10 text-[var(--primary)]">
              <Layers className="h-4 w-4" />
            </div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              {block.title ?? 'Process Flow & Architecture'}
            </h3>
          </div>
          <span className="rounded-full bg-[var(--surface-alt)] px-2.5 py-0.5 text-xs font-medium text-[var(--text-muted)]">
            {parsedSteps.length} Steps
          </span>
        </div>

        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm space-y-3">
          <p className="text-xs uppercase tracking-wider font-semibold text-[var(--primary)]">
            Visual Execution Sequence
          </p>

          <div className="flex flex-col items-center gap-2 pt-2">
            {parsedSteps.map((s, idx) => (
              <div key={s.step} className="w-full flex flex-col items-center">
                <div className="w-full max-w-xl rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4 transition hover:border-[var(--primary)]/50">
                  <div className="flex items-start gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--primary)] text-xs font-bold text-white shadow-sm">
                      {s.step}
                    </span>
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-[var(--text-primary)]">
                        {s.title}
                      </p>
                      {s.detail && (
                        <p className="text-xs leading-relaxed text-[var(--text-secondary)]">
                          {s.detail}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {idx < parsedSteps.length - 1 && (
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

  // Case 4: General text fallback in diagram styling or empty state
  return (
    <section className="space-y-3">
      {block.title && (
        <h3 className="text-base font-semibold text-[var(--text-primary)]">
          {block.title}
        </h3>
      )}

      {rawContent ? (
        <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface-alt)] p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <Workflow className="h-4 w-4 text-[var(--primary)]" />
            <span className="text-xs font-semibold uppercase tracking-wider text-[var(--primary)]">
              Diagram Overview
            </span>
          </div>
          <p className="whitespace-pre-line text-sm leading-relaxed text-[var(--text-primary)]">
            {rawContent.replace(/^Renderer\s*Type:\s*Diagram\.?\s*/i, '').trim()}
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
