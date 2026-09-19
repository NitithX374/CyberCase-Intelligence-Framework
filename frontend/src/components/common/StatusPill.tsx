import type { ReactNode } from "react";

export type StatusPillTone =
  "neutral" | "positive" | "attention" | "critical" | "external" | "source";

interface StatusPillProps {
  children: ReactNode;
  tone?: StatusPillTone;
  className?: string;
}

const toneClasses: Record<StatusPillTone, string> = {
  neutral: "text-ink-secondary",
  positive: "text-established",
  attention: "text-unresolved",
  critical: "text-critical",
  external: "text-mitre",
  source: "text-source",
};

export function StatusPill({ children, tone = "neutral", className = "" }: StatusPillProps) {
  return (
    <span
      className={`inline-flex items-center text-[11px] font-medium leading-4 ${toneClasses[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
