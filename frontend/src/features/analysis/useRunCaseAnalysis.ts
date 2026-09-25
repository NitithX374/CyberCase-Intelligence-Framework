"use client";

import { useEffect, useEffectEvent } from "react";
import {
  matchMutation,
  useQueryClient,
  type MutationCacheNotifyEvent,
} from "@tanstack/react-query";
import type { AnalysisStepRead } from "@/lib/api";
import { caseQueryKeys } from "@/lib/queryKeys";
import { useIsCaseAnalysisRunning, useStartCaseAnalysis } from "./queries";

export function useRunCaseAnalysis(caseId: string) {
  const startAnalysis = useStartCaseAnalysis(caseId);
  const isRunning = useIsCaseAnalysisRunning(caseId);

  return () => {
    if (!isRunning) startAnalysis.mutate();
  };
}

interface AnalysisRunOutcome {
  onCompleted: () => void;
  onQuestion: () => void;
  onFailed: (error: unknown) => void;
}

export function useAnalysisRunOutcome(caseId: string, outcome: AnalysisRunOutcome) {
  const queryClient = useQueryClient();
  const settle = useEffectEvent((event: MutationCacheNotifyEvent) => {
    if (event.type !== "updated") return;
    const run = { mutationKey: caseQueryKeys.analysisRun(caseId), exact: true };
    if (!matchMutation(run, event.mutation)) return;
    if (event.action.type === "error") outcome.onFailed(event.action.error);
    if (event.action.type !== "success") return;
    const step: AnalysisStepRead = event.action.data;
    if (step.status === "need_followup") outcome.onQuestion();
    else outcome.onCompleted();
  });

  useEffect(
    () => queryClient.getMutationCache().subscribe((event) => settle(event)),
    [queryClient],
  );
}
