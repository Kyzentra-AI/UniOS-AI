import type { CSSProperties, ReactNode } from "react";

export const stagger = (i: number) => ({ "--i": i }) as CSSProperties;

const icon = {
  fill: "none",
  stroke: "currentColor",
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
} as const;

export function Chevron({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={`h-4 w-4 ${className}`} strokeWidth="1.8" {...icon}>
      <path d="M6 3.5 10.5 8 6 12.5" />
    </svg>
  );
}

export function Check({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={`h-3.5 w-3.5 ${className}`} strokeWidth="2.2" {...icon}>
      <path d="m3.5 8.5 3 3 6-7" />
    </svg>
  );
}

export function Clock({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={`h-3.5 w-3.5 ${className}`} strokeWidth="1.6" {...icon}>
      <circle cx="8" cy="8" r="6" />
      <path d="M8 4.8V8l2.2 1.4" />
    </svg>
  );
}

export function ProgressRing({
  value,
  size = 96,
  stroke = 8,
}: {
  value: number;
  size?: number;
  stroke?: number;
}) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const o = c * (1 - Math.min(100, Math.max(0, value)) / 100);

  return (
    <div
      className="relative shrink-0"
      style={{ width: size, height: size }}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label="Overall progress"
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--border)" strokeWidth={stroke} />
        <circle
          className="ring-draw"
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--primary)"
          strokeWidth={stroke}
          strokeLinecap="round"
          style={{ "--c": c, "--o": o } as CSSProperties}
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center font-bold tracking-tight text-[var(--text-primary)]"
        style={{ fontSize: size * 0.25 }}>
        {value}%
      </span>
    </div>
  );
}

/** Timeline node: done = filled, active = pulsing, idle = hollow */
export function Node({
  state,
  tone = "blue",
  children,
}: {
  state: "done" | "active" | "idle";
  tone?: "blue" | "orange";
  children?: ReactNode;
}) {
  const accent = tone === "orange" ? "var(--feature-orange)" : "var(--feature-blue)";
  const soft = tone === "orange" ? "var(--feature-orange-soft)" : "var(--feature-blue-soft)";

  const style: CSSProperties =
    state === "done"
      ? { backgroundColor: "var(--primary)", borderColor: "var(--primary)", color: "var(--surface)" }
      : state === "active"
        ? { backgroundColor: soft, borderColor: accent, color: accent }
        : { backgroundColor: "var(--surface)", borderColor: "var(--border)", color: "var(--text-muted)" };

  return (
    <span
      className={`pop relative z-10 flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold ${
        state === "active" ? "pulse" : ""
      }`}
      style={style}
    >
      {state === "done" ? <Check /> : children}
    </span>
  );
}