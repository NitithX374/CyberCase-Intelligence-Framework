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
  listCaseClarifications,
  listCaseDocuments,
  listCaseEvidence,
  listCases,
  updateCase,
  type CaseRead,
  type CaseAnalysisResultRead,
  type CaseClarificationRead,
  type CaseDocumentRead,
  type EvidenceSourceRead,
} from "@/lib/api";
import { chatQueryKeys } from "./useChatQueries";

export const caseQueryKeys = {
  all: ["cases"] as const,
  cases: () => [...caseQueryKeys.all, "list"] as const,
  case: (caseId: string) => [...caseQueryKeys.all, caseId] as const,
  documents: (caseId: string) => [...caseQueryKeys.case(caseId), "documents"] as const,
  evidence: (caseId: string) => [...caseQueryKeys.case(caseId), "evidence"] as const,
  analysis: (caseId: string) => [...caseQueryKeys.case(caseId), "analysis"] as const,
  clarifications: (caseId: string) => [...caseQueryKeys.case(caseId), "clarifications"] as const,
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
  return useQuery<EvidenceSourceRead[]>({
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

export function useCaseClarifications(caseId: string | null) {
  return useQuery<CaseClarificationRead[]>({
    queryKey: caseQueryKeys.clarifications(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseClarifications(caseId!, signal),
    enabled: caseId !== null,
    retry: false,
  });
}

export function useCaseWorkspaceQueries(caseId: string | null) {
  const documents = useCaseDocuments(caseId);
  const evidence = useCaseEvidence(caseId);
  const analysis = useCaseAnalysis(caseId);
  const clarifications = useCaseClarifications(caseId);
  return { documents, evidence, analysis, clarifications };
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
    onSuccess: (_deleted, deletedCaseId) => {
      queryClient.setQueryData<CaseRead[]>(
        caseQueryKeys.cases(),
        (current) => (current ?? []).filter((item) => item.id !== deletedCaseId),
      );
      queryClient.removeQueries({ queryKey: caseQueryKeys.case(deletedCaseId) });
      queryClient.removeQueries({ queryKey: chatQueryKeys.thread(deletedCaseId) });
    },
  });

  return { createMutation, updateMutation, deleteMutation, upsertCase };
}
