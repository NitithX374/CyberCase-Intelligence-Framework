import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useCallback, useEffect, useRef } from "react";
import {
  createCase,
  deleteCase,
  getCaseRun,
  getCaseAnalysis,
  listCaseDocuments,
  listCaseEvidence,
  listCaseFollowUps,
  listCases,
  updateCase,
  type CaseRead,
  type CaseAnalysisResultRead,
  type CaseDocumentRead,
  type CaseFollowUpRead,
  type CaseSourceRead,
  type CaseRunRead,
} from "@/lib/api";

export const caseQueryKeys = {
  all: ["cases"] as const,
  cases: () => [...caseQueryKeys.all, "list"] as const,
  case: (caseId: string) => [...caseQueryKeys.all, caseId] as const,
  chat: (caseId: string) => [...caseQueryKeys.case(caseId), "chat"] as const,
  documents: (caseId: string) => [...caseQueryKeys.case(caseId), "documents"] as const,
  evidence: (caseId: string) => [...caseQueryKeys.case(caseId), "evidence"] as const,
  analysis: (caseId: string) => [...caseQueryKeys.case(caseId), "analysis"] as const,
  followups: (caseId: string) => [...caseQueryKeys.case(caseId), "followups"] as const,
  run: (caseId: string, runId: string) => [...caseQueryKeys.case(caseId), "runs", runId] as const,
  reports: (caseId: string) => [...caseQueryKeys.case(caseId), "reports"] as const,
};

function sortCases(cases: CaseRead[]): CaseRead[] {
  return [...cases].sort(
    (left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at),
  );
}

export function useCaseDocuments(caseId: string | null) {
  return useQuery<CaseDocumentRead[]>({
    queryKey: caseQueryKeys.documents(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseDocuments(caseId!, signal),
    enabled: caseId !== null,
    retry: false,
  });
}

export function useCaseEvidence(caseId: string | null) {
  return useQuery<CaseSourceRead[]>({
    queryKey: caseQueryKeys.evidence(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseEvidence(caseId!, signal),
    enabled: caseId !== null,
    retry: false,
  });
}

export function useCaseAnalysis(caseId: string | null) {
  return useQuery<CaseAnalysisResultRead | null>({
    queryKey: caseQueryKeys.analysis(caseId ?? "none"),
    queryFn: ({ signal }) => getCaseAnalysis(caseId!, signal),
    enabled: caseId !== null,
    retry: false,
  });
}

export function useCaseFollowUps(caseId: string | null) {
  return useQuery<CaseFollowUpRead[]>({
    queryKey: caseQueryKeys.followups(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseFollowUps(caseId!, signal),
    enabled: caseId !== null,
    retry: false,
  });
}

export function useCases() {
  return useQuery({
    queryKey: caseQueryKeys.cases(),
    queryFn: ({ signal }) => listCases(signal),
    retry: false,
  });
}

export function useCaseRunPolling(
  caseId: string | null,
  runId: string | null | undefined,
  caseChatId: string | null | undefined,
) {
  const queryClient = useQueryClient();
  const lastInvalidated = useRef<string | null>(null);
  const query = useQuery<CaseRunRead>({
    queryKey: caseQueryKeys.run(caseId ?? "none", runId ?? "none"),
    queryFn: ({ signal }) => getCaseRun(caseId!, runId!, signal),
    enabled: Boolean(caseId && runId),
    retry: false,
    refetchInterval: (currentQuery) => {
      const status = currentQuery.state.data?.status;
      return status === "queued" || status === "running" ? 1500 : false;
    },
  });

  useEffect(() => {
    const status = query.data?.status;
    if (!caseId || !runId || (status !== "completed" && status !== "failed")) return;
    const attemptCount = query.data?.attempt_count ?? 0;
    const invalidationKey = `${runId}:${attemptCount}:${status}`;
    if (lastInvalidated.current === invalidationKey) return;
    lastInvalidated.current = invalidationKey;
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() });
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId) });
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.analysis(caseId) });
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(caseId) });
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.followups(caseId) });
    if (caseChatId) {
      void queryClient.refetchQueries({ queryKey: caseQueryKeys.chat(caseChatId), exact: true, type: "all" });
    }
  }, [caseChatId, caseId, query.data?.status, query.data?.attempt_count, queryClient, runId]);

  return query;
}

export function useCaseMutations() {
  const queryClient = useQueryClient();

  const upsertCase = useCallback((caseRecord: CaseRead) => {
    queryClient.setQueryData<CaseRead[]>(
      caseQueryKeys.cases(),
      (current) =>
        sortCases([
          {
            ...current?.find((item) => item.id === caseRecord.id),
            ...caseRecord,
          },
          ...(current ?? []).filter((item) => item.id !== caseRecord.id),
        ]),
    );
  }, [queryClient]);

  const createMutation = useMutation({
    mutationFn: () => createCase(),
    onSuccess: upsertCase,
  });
  const updateMutation = useMutation({
    mutationFn: ({ caseId, title }: { caseId: string; title: string }) =>
      updateCase(caseId, title),
    onSuccess: upsertCase,
  });
  const deleteMutation = useMutation({
    mutationFn: (caseId: string) => deleteCase(caseId),
    onSuccess: (_deleted, deletedCaseId) => {
      queryClient.setQueryData<CaseRead[]>(
        caseQueryKeys.cases(),
        (current) => (current ?? []).filter((item) => item.id !== deletedCaseId),
      );
      queryClient.removeQueries({ queryKey: caseQueryKeys.case(deletedCaseId) });
      queryClient.removeQueries({ queryKey: caseQueryKeys.chat(deletedCaseId) });
    },
  });

  return { createMutation, updateMutation, deleteMutation, upsertCase };
}
