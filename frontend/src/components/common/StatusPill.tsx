import type { ReactNode } from "react";

export type StatusPillTone =
  | "neutral"
  | "positive"
  | "attention"
  | "critical"
  | "external"
  | "evidence";

interface StatusPillProps {
  children: ReactNode;
  tone?: StatusPillTone;
  className?: string;
}

const toneClasses: Record<StatusPillTone, string> = {
  neutral: "border-line bg-surface-nested text-ink-secondary",
  positive: "border-established/30 bg-established/10 text-established",
  attention: "border-unresolved/30 bg-unresolved/10 text-unresolved",
  critical: "border-critical/30 bg-critical/10 text-critical",
  external: "border-mitre/25 bg-mitre/10 text-mitre",
  evidence: "border-evidence/25 bg-evidence/10 text-evidence",
};

export function StatusPill({
  children,
  tone = "neutral",
  className = "",
}: StatusPillProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold leading-4 ${toneClasses[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
