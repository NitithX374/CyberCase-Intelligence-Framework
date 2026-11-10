"use client";

import { useEffect, useState } from "react";
import { Icon } from "@/components/icons";
import {
  formatElapsed,
  progressStages,
  useAnalysisProgress,
  type ProgressRow,
  type ProgressStage,
} from "./progress";

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

  const stages = progressStages(reached, now ?? reached[reached.length - 1].reachedAt);
  return (
    <ol
      aria-label="Analysis progress"
      className={`flex w-full items-start overflow-x-auto pt-1 pb-2 text-center ${className}`}
    >
      {stages.map((stage, index) => (
        <li
          key={stage.key}
          aria-current={stage.state === "current" ? "step" : undefined}
          className={`relative flex flex-1 flex-col items-center px-2 ${
            stage.rows.length > 1 ? "min-w-[12.5rem]" : "min-w-[8.5rem]"
          }`}
        >
          {index > 0 && (
            <span
              aria-hidden="true"
              className="absolute top-[18px] right-1/2 h-0.5 w-full overflow-hidden bg-line-strong"
            >
              {stage.state !== "waiting" && (
                <span className="grow-x block h-full w-full bg-primary" />
              )}
            </span>
          )}
          <StageNode stage={stage} number={index + 1} />
          {stage.rows.length > 1 ? (
            <>
              <span className="mt-2 text-xs font-semibold tracking-[0.06em] text-ink-muted uppercase">
                At the same time
              </span>
              <ul className="mt-1.5 flex flex-col gap-1.5 text-left whitespace-nowrap">
                {stage.rows.map((row) => (
                  <li key={row.step} className={`flex items-center gap-1.5 ${rowText(row)}`}>
                    <span
                      aria-hidden="true"
                      className={`h-2 w-2 shrink-0 rounded-full ${
                        row.state === "waiting" ? "bg-line-strong" : "bg-primary"
                      }`}
                    />
                    {row.label}
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <span className={`mt-2 ${rowText(stage.rows[0])}`}>{stage.rows[0].label}</span>
          )}
          {stage.seconds !== null && (
            <span className="mt-1 text-xs text-ink-muted tabular-nums">
              {formatElapsed(stage.seconds)}
            </span>
          )}
        </li>
      ))}
    </ol>
  );
}

function StageNode({ stage, number }: { stage: ProgressStage; number: number }) {
  if (stage.state === "done") {
    return (
      <span className="pop-in relative flex h-9 w-9 items-center justify-center rounded-full bg-primary text-white">
        <Icon name="check" className="text-xl" />
      </span>
    );
  }
  if (stage.state === "current") {
    return (
      <span className="node-pulse relative flex h-9 w-9 items-center justify-center rounded-full border-2 border-primary bg-surface text-primary">
        <Icon name="spinner" className="text-lg" />
      </span>
    );
  }
  return (
    <span className="relative flex h-9 w-9 items-center justify-center rounded-full border-2 border-line-strong bg-surface text-xs font-semibold text-ink-muted">
      {number}
    </span>
  );
}

function rowText(row: ProgressRow): string {
  return `text-sm leading-5 ${
    row.state === "waiting"
      ? "text-ink-muted"
      : row.state === "current"
        ? "font-semibold text-ink"
        : "text-ink-secondary"
  }`;
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
