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

// No case, no run: a key nothing is ever started under, so the filter below
// can be written once instead of branching on a null case.
const UNRUNNABLE_ANALYSIS_KEY = ["cases", "__no_case__", "analysis", "run"] as const;

/** Whether this case has an analysis in flight, wherever it was started from.
 *
 * `useMutation().isPending` belongs to one component: leave the page and the
 * observer goes with it, so the header came back offering to run an analysis
 * that was still running. The mutation itself outlives the component in the
 * cache, so ask the cache instead, by case.
 *
 * This survives navigation inside the app, not a reload -- the cache is in
 * memory, and the backend keeps no row for a run in progress.
 */
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
    // The key is what makes the run findable from anywhere. onSuccess below
    // stays a hook option on purpose: query-core calls the mutation's own
    // options even after the component that started it is gone, so the caches
    // are refreshed whether or not the reader is still looking at this case.
    mutationKey: caseId ? caseQueryKeys.analysisRun(caseId) : UNRUNNABLE_ANALYSIS_KEY,
    mutationFn: (request: CaseAnalysisCreate) => {
      if (!caseId) throw new Error("Case ID is required to start analysis.");
      return startCaseAnalysis(caseId, request);
    },
    onSuccess: (step: AnalysisStepRead) => {
      if (!caseId) return;
      // A step that paused to ask something carries no result, and writing its
      // envelope into the analysis cache would show the reader a half-finished
      // analysis as a finished one. The question it asked arrives with the chat
      // refetch below.
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
