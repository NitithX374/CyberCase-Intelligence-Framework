import { useQuery, type QueryClient } from "@tanstack/react-query";
import type { StreamedStep } from "@/lib/api/stream";
import { caseQueryKeys } from "@/lib/queryKeys";

export type AnalysisStepName = "assess" | "gate" | "retrieve" | "read" | "judge" | "bind";

export interface ReachedStep {
  step: AnalysisStepName;
  elapsed: number;
  reachedAt: number;
}

export interface ProgressRow {
  step: AnalysisStepName;
  label: string;
  state: "done" | "current" | "waiting";
  seconds: number | null;
}

const STEP_LABELS: Record<AnalysisStepName, string> = {
  assess: "Checking what the case is missing",
  gate: "Checking whether ATT&CK applies",
  retrieve: "Retrieving ATT&CK context",
  read: "Reading the sources: claims and quotations",
  judge: "Judging: summary, open questions, ATT&CK",
  bind: "Checking the quotations against the sources",
};

const PLANNED: AnalysisStepName[] = ["assess", "gate", "read", "bind", "judge"];

function isStepName(step: string): step is AnalysisStepName {
  return step in STEP_LABELS;
}

export function recordStep(queryClient: QueryClient, caseId: string, reached: StreamedStep) {
  const { step, elapsed } = reached;
  if (!isStepName(step)) return;
  queryClient.setQueryData<ReachedStep[]>(caseQueryKeys.analysisProgress(caseId), (steps = []) => [
    ...steps,
    { step, elapsed, reachedAt: Date.now() },
  ]);
}

export function clearProgress(queryClient: QueryClient, caseId: string) {
  queryClient.setQueryData<ReachedStep[]>(caseQueryKeys.analysisProgress(caseId), []);
}

export function useAnalysisProgress(caseId: string | null): ReachedStep[] {
  const { data } = useQuery<ReachedStep[]>({
    queryKey: caseQueryKeys.analysisProgress(caseId ?? "none"),
    queryFn: () => [],
    enabled: false,
    staleTime: Infinity,
  });
  return data ?? [];
}

export function progressRows(reached: ReachedStep[], now: number): ProgressRow[] {
  const order = PLANNED.flatMap((step): AnalysisStepName[] =>
    step === "gate" && reached.some((r) => r.step === "retrieve") ? ["gate", "retrieve"] : [step],
  );
  return order.map((step) => {
    const label = STEP_LABELS[step];
    const index = reached.findIndex((r) => r.step === step);
    if (index < 0) return { step, label, state: "waiting", seconds: null };
    const next = reached[index + 1];
    if (next) return { step, label, state: "done", seconds: next.elapsed - reached[index].elapsed };
    return {
      step,
      label,
      state: "current",
      seconds: Math.max(0, (now - reached[index].reachedAt) / 1000),
    };
  });
}

export function formatElapsed(seconds: number): string {
  const whole = Math.floor(seconds);
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
}
