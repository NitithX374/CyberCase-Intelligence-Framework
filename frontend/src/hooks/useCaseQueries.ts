import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useCallback } from "react";
import {
  createCase,
  deleteCase,
  getCaseAnalysis,
  getCaseEvidenceSnapshot,
  listCaseClarifications,
  listCaseDocuments,
  listCaseEvidence,
  listCases,
  updateCase,
  type CaseRead,
  type CaseAnalysisResultRead,
  type CaseClarificationRead,
  type CaseDocumentRead,
  type CaseEvidenceSnapshotRead,
  type EvidenceSourceRead,
  type ChatThreadRead,
} from "@/lib/api";
import { chatQueryKeys } from "./useChatQueries";

export const caseQueryKeys = {
  all: ["cases"] as const,
  cases: () => [...caseQueryKeys.all, "list"] as const,
  case: (caseId: string) => [...caseQueryKeys.all, caseId] as const,
  documents: (caseId: string) => [...caseQueryKeys.case(caseId), "documents"] as const,
  evidence: (caseId: string) => [...caseQueryKeys.case(caseId), "evidence"] as const,
  analysis: (caseId: string) => [...caseQueryKeys.case(caseId), "analysis"] as const,
  snapshot: (caseId: string, snapshotId: string) => [...caseQueryKeys.case(caseId), "snapshots", snapshotId] as const,
  clarifications: (caseId: string) => [...caseQueryKeys.case(caseId), "clarifications"] as const,
  run: (caseId: string, runId: string) => [...caseQueryKeys.case(caseId), "runs", runId] as const,
  reports: (caseId: string) => [...caseQueryKeys.case(caseId), "reports"] as const,
};

function sortCases(cases: CaseRead[]): CaseRead[] {
  return [...cases].sort(
    (left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at),
  );
}

export function useCaseWorkspaceQueries(
  caseId: string | null,
) {
  const enabled = caseId !== null;
  const documents = useQuery<CaseDocumentRead[]>({
    queryKey: caseQueryKeys.documents(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseDocuments(caseId!, signal),
    enabled,
    retry: false,
  });
  const evidence = useQuery<EvidenceSourceRead[]>({
    queryKey: caseQueryKeys.evidence(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseEvidence(caseId!, signal),
    enabled,
    retry: false,
  });
  const analysis = useQuery<CaseAnalysisResultRead | null>({
    queryKey: caseQueryKeys.analysis(caseId ?? "none"),
    queryFn: ({ signal }) => getCaseAnalysis(caseId!, signal),
    enabled,
    retry: false,
  });
  const snapshot = useQuery<CaseEvidenceSnapshotRead>({
    queryKey: caseQueryKeys.snapshot(caseId ?? "none", analysis.data?.snapshot_id ?? "none"),
    queryFn: ({ signal }) => getCaseEvidenceSnapshot(caseId!, analysis.data!.snapshot_id, signal),
    enabled: enabled && analysis.data?.snapshot_id !== undefined,
    retry: false,
  });
  const clarifications = useQuery<CaseClarificationRead[]>({
    queryKey: caseQueryKeys.clarifications(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseClarifications(caseId!, signal),
    enabled,
    retry: false,
  });
  return { documents, evidence, analysis, snapshot, clarifications };
}

/**
 * @deprecated Synthesizing CaseRead from ChatThreadRead violates Case-ownership architecture.
 * Deprecated as part of Pragmatic Lean hotfix separating Case Analysis from Chat Q&A.
 */
export function caseFromChatThread(thread: ChatThreadRead): CaseRead {
  return {
    id: thread.id,
    user_id: thread.user_id ?? null,
    title: thread.title,
    status: thread.status,
    chat_thread_id: thread.id,
    created_at: thread.created_at,
    updated_at: thread.updated_at,
  };
}

export function useCases() {
  return useQuery({
    queryKey: caseQueryKeys.cases(),
    queryFn: ({ signal }) => listCases(signal),
    retry: false,
  });
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
    onSuccess: (_value, caseId) => {
      queryClient.setQueryData<CaseRead[]>(
        caseQueryKeys.cases(),
        (current) => (current ?? []).filter((item) => item.id !== caseId),
      );
      queryClient.removeQueries({ queryKey: caseQueryKeys.case(caseId) });
      queryClient.removeQueries({ queryKey: chatQueryKeys.thread(caseId) });
    },
  });

  return {
    upsertCase,
    createMutation,
    updateMutation,
    deleteMutation,
  };
}
