import { useMutation, useMutationState, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getCaseAnalysis,
  startCaseAnalysis,
  type AnalysisStepRead,
  type CaseAnalysisCreate,
  type CaseAnalysisResultRead,
} from "@/lib/api";
import { caseQueryKeys } from "@/lib/queryKeys";

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

export function useStartCaseAnalysis(caseId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: caseId ? caseQueryKeys.analysisRun(caseId) : UNRUNNABLE_ANALYSIS_KEY,
    mutationFn: (request: CaseAnalysisCreate) => {
      if (!caseId) throw new Error("Case ID is required to start analysis.");
      return startCaseAnalysis(caseId, request);
    },
    onSuccess: (step: AnalysisStepRead) => {
      if (!caseId) return;
      if (step.status === "completed" && step.result) {
        queryClient.setQueryData(caseQueryKeys.analysis(caseId), step.result);
      }
      void Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId), exact: true }),
        queryClient.refetchQueries({ queryKey: caseQueryKeys.chat(caseId), exact: true }),
      ]);
    },
  });
}
