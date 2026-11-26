
"use client";

import { useEffect, useId, useState } from "react";
import mermaid from "mermaid";

interface MermaidDiagramProps {
  chart: string;
}

export default function MermaidDiagram({ chart }: MermaidDiagramProps) {
  const reactId = useId().replace(/[^a-zA-Z0-9_-]/g, "");
  const [svg, setSvg] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function renderDiagram() {
      setSvg("");
      setError(false);

      try {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict",
          theme: "neutral",
          flowchart: {
            useMaxWidth: false,
            htmlLabels: true,
          },
        });

        const result = await mermaid.render(
          `mermaid-${reactId}`,
          chart.trim(),
        );

        if (!cancelled) {
          setSvg(result.svg);
        }
      } catch {
        if (!cancelled) {
          setError(true);
        }
      }
    }

    if (chart.trim()) {
      void renderDiagram();
    } else {
      setError(true);
    }

    return () => {
      cancelled = true;
    };
  }, [chart, reactId]);

  if (error) {
    return (
      <div className="min-w-0 space-y-2 rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-alt)] p-4">
        <p className="text-xs font-semibold text-[var(--text-muted)]">
          Diagram preview unavailable — source shown below
        </p>

        <pre className="max-w-full overflow-x-auto whitespace-pre text-xs leading-6 text-[var(--text-secondary)]">
          {chart}
        </pre>
      </div>
    );
  }

  if (!svg) {
    return (
      <div
        className="flex min-h-32 w-full items-center justify-center rounded-xl bg-[var(--surface-alt)] text-sm text-[var(--text-muted)]"
        role="status"
      >
        Rendering diagram...
      </div>
    );
  }

  return (
    <div
      className="w-full min-w-0 max-w-full overflow-auto rounded-xl border border-[var(--border)] bg-white p-3 sm:p-4"
      aria-label="Mermaid diagram"
    >
      <div
        className="mx-auto w-max min-w-full"
        dangerouslySetInnerHTML={{ __html: svg }}
      />

      <style jsx>{`
        div :global(svg) {
          display: block;
          width: auto;
          height: auto;
          max-width: none;
        }
      `}</style>
    </div>
  );
}
