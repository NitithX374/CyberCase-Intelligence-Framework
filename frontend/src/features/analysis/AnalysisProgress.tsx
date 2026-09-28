"use client";

import { useEffect, useState } from "react";
import { formatElapsed, progressRows, useAnalysisProgress } from "./progress";

export function AnalysisProgress({
  caseId,
  className = "",
}: {
  caseId: string;
  className?: string;
}) {
  const reached = useAnalysisProgress(caseId);
  const now = useClock(reached.length > 0);
  if (reached.length === 0) return null;

  const rows = progressRows(reached, now ?? reached[reached.length - 1].reachedAt);
  return (
    <ol
      aria-label="Analysis progress"
      className={`w-full max-w-sm space-y-1.5 text-left ${className}`}
    >
      {rows.map((row) => (
        <li
          key={row.step}
          aria-current={row.state === "current" ? "step" : undefined}
          className={`flex items-baseline justify-between gap-6 text-[13px] leading-5 ${
            row.state === "waiting"
              ? "text-ink-muted"
              : row.state === "current"
                ? "font-medium text-ink"
                : "text-ink-secondary"
          }`}
        >
          <span>{row.label}</span>
          {row.seconds !== null && (
            <span className="shrink-0 tabular-nums">{formatElapsed(row.seconds)}</span>
          )}
        </li>
      ))}
    </ol>
  );
}

function useClock(running: boolean): number | null {
  const [now, setNow] = useState<number | null>(null);
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [running]);
  return now;
}
