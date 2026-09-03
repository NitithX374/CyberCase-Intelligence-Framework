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
  neutral: "text-ink-secondary",
  positive: "text-established",
  attention: "text-unresolved",
  critical: "text-critical",
  external: "text-mitre",
  evidence: "text-evidence",
};

export function StatusPill({
  children,
  tone = "neutral",
  className = "",
}: StatusPillProps) {
  return (
    <span
      className={`inline-flex items-center text-[11px] font-medium leading-4 ${toneClasses[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
