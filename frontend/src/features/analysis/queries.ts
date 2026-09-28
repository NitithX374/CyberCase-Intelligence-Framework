import { useMutation, useMutationState, useQuery, useQueryClient } from "@tanstack/react-query";
import { getCaseAnalysis, startCaseAnalysis } from "./api";
import { clearProgress, recordStep } from "./progress";
import type { AnalysisStepRead, CaseAnalysisResultRead } from "@/lib/api/types";
import { caseQueryKeys } from "@/lib/queryKeys";
import { useIsFollowupPending } from "@/features/chat/useCaseChat";

export function useCaseAnalysis(caseId: string | null) {
  return useQuery<CaseAnalysisResultRead | null>({
    queryKey: caseQueryKeys.analysis(caseId ?? "none"),
    queryFn: ({ signal }) => getCaseAnalysis(caseId!, signal),
    enabled: caseId !== null,
    retry: false,
  });
}

const UNRUNNABLE_ANALYSIS_KEY = ["cases", "__no_case__", "analysis", "run"] as const;

export function useIsCaseAnalysisRunning(caseId: string | null): boolean {
  const running = useMutationState({
    filters: {
      mutationKey: caseId ? caseQueryKeys.analysisRun(caseId) : UNRUNNABLE_ANALYSIS_KEY,
      exact: true,
      status: "pending",
    },
    select: (mutation) => mutation.mutationId,
  });
  return running.length > 0;
}

export function useIsAnalysisUpdating(caseId: string | null): boolean {
  const running = useIsCaseAnalysisRunning(caseId);
  const answering = useIsFollowupPending(caseId);
  return running || answering;
}

export function useStartCaseAnalysis(caseId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: caseId ? caseQueryKeys.analysisRun(caseId) : UNRUNNABLE_ANALYSIS_KEY,
    mutationFn: () => {
      if (!caseId) throw new Error("Case ID is required to start analysis.");
      return startCaseAnalysis(caseId, (step) => recordStep(queryClient, caseId, step));
    },
    onMutate: () => {
      if (caseId) clearProgress(queryClient, caseId);
    },
    onSuccess: (step: AnalysisStepRead) => {
      if (caseId && step.status === "completed" && step.result) {
        queryClient.setQueryData(caseQueryKeys.analysis(caseId), step.result);
      }
    },
    onSettled: (_step, error) => {
      if (!caseId) return;
      clearProgress(queryClient, caseId);
      void Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId), exact: true }),
        queryClient.refetchQueries({ queryKey: caseQueryKeys.chat(caseId), exact: true }),
        ...(error
          ? [
              queryClient.invalidateQueries({
                queryKey: caseQueryKeys.analysis(caseId),
                exact: true,
              }),
            ]
          : []),
      ]);
    },
  });
}
