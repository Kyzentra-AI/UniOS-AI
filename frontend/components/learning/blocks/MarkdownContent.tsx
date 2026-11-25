
"use client";

import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

import MermaidDiagram from "./MermaidDiagram";

interface MarkdownContentProps {
  content: string;
  className?: string;
}

function normalizeMarkdown(value: string): string {
  let content = value.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

  // Recover a common malformed response containing an unclosed code fence.
  const fenceCount = (content.match(/^[ \t]*```/gm) ?? []).length;

  if (fenceCount % 2 !== 0) {
    content = `${content}\n\`\`\``;
  }

  return content;
}

const components: Components = {
  h1: ({ children }) => (
    <h2 className="mt-6 text-xl font-bold text-[var(--text-primary)]">
      {children}
    </h2>
  ),

  h2: ({ children }) => (
    <h3 className="mt-5 text-lg font-semibold text-[var(--text-primary)]">
      {children}
    </h3>
  ),

  h3: ({ children }) => (
    <h4 className="mt-4 text-base font-semibold text-[var(--text-primary)]">
      {children}
    </h4>
  ),

  p: ({ children }) => (
    <p className="text-sm leading-7 text-[var(--text-secondary)]">
      {children}
    </p>
  ),

  ul: ({ children }) => (
    <ul className="my-4 list-disc space-y-2 pl-5 text-sm leading-7 text-[var(--text-secondary)] marker:text-[var(--primary)]">
      {children}
    </ul>
  ),

  ol: ({ children }) => (
    <ol className="my-4 list-decimal space-y-2 pl-5 text-sm leading-7 text-[var(--text-secondary)] marker:text-[var(--primary)]">
      {children}
    </ol>
  ),

  li: ({ children }) => (
    <li className="pl-1">{children}</li>
  ),

  strong: ({ children }) => (
    <strong className="font-semibold text-[var(--text-primary)]">
      {children}
    </strong>
  ),

  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-[var(--primary)] bg-[var(--surface-alt)] py-2 pl-4 pr-3 text-sm leading-7 text-[var(--text-secondary)]">
      {children}
    </blockquote>
  ),

  table: ({ children }) => (
    <div className="my-4 overflow-x-auto rounded-xl border border-[var(--border)]">
      <table className="w-full border-collapse text-left text-sm">
        {children}
      </table>
    </div>
  ),

  thead: ({ children }) => (
    <thead className="bg-[var(--surface-alt)] text-[var(--text-primary)]">
      {children}
    </thead>
  ),

  th: ({ children }) => (
    <th className="border-b border-[var(--border)] px-4 py-3 font-semibold">
      {children}
    </th>
  ),

  td: ({ children }) => (
    <td className="border-b border-[var(--border)] px-4 py-3 text-[var(--text-secondary)]">
      {children}
    </td>
  ),

  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="font-medium text-[var(--primary)] underline underline-offset-2 hover:opacity-80"
    >
      {children}
    </a>
  ),

  code: ({ className, children, ...props }) => {
    const language = /language-([\w-]+)/.exec(className ?? "")?.[1];
    const value = String(children).replace(/\n$/, "");

    if (language === "mermaid") {
      return <MermaidDiagram chart={value} />;
    }

    if (!className) {
      return (
        <code
          className="rounded-md bg-[var(--surface-alt)] px-1.5 py-0.5 font-mono text-[0.9em] text-[var(--primary)]"
          {...props}
        >
          {children}
        </code>
      );
    }

    return (
      <code className={`hljs ${className}`} {...props}>
        {children}
      </code>
    );
  },

  pre: ({ children }) => (
    <div className="my-4 overflow-x-auto rounded-xl border border-[var(--border)] bg-[#18343A] p-4 text-sm leading-6 text-white [&_code]:font-mono [&_code]:text-white">
      <pre className="whitespace-pre">
        {children}
      </pre>
    </div>
  ),

  hr: () => (
    <hr className="my-5 border-[var(--border)]" />
  ),
};

export default function MarkdownContent({
  content,
  className = "",
}: MarkdownContentProps) {
  const normalized = normalizeMarkdown(content);

  if (!normalized.trim()) {
    return (
      <p className="text-sm leading-7 text-[var(--text-muted)]">
        No content is available for this section.
      </p>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={components}
      >
        {normalized}
      </ReactMarkdown>
    </div>
  );
}