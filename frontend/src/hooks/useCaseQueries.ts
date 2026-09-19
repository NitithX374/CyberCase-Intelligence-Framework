import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import {
  createCase,
  deleteCase,
  getCase,
  getCaseAnalysis,
  listCaseDocuments,
  listCaseSources,
  listCases,
  startCaseAnalysis,
  updateCase,
  uploadCaseDocument,
  type CaseRead,
  type CaseAnalysisCreate,
  type CaseAnalysisResultRead,
  type CaseDocumentRead,
  type CaseSourceRead,
} from "@/lib/api";

export const caseQueryKeys = {
  all: ["cases"] as const,
  cases: () => [...caseQueryKeys.all, "list"] as const,
  case: (caseId: string) => [...caseQueryKeys.all, caseId] as const,
  chat: (caseId: string) => [...caseQueryKeys.case(caseId), "chat"] as const,
  documents: (caseId: string) => [...caseQueryKeys.case(caseId), "documents"] as const,
  sources: (caseId: string) => [...caseQueryKeys.case(caseId), "sources"] as const,
  analysis: (caseId: string) => [...caseQueryKeys.case(caseId), "analysis"] as const,
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

export function useCaseSources(caseId: string | null) {
  return useQuery<CaseSourceRead[]>({
    queryKey: caseQueryKeys.sources(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseSources(caseId!, signal),
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

export function useCase(caseId: string | null) {
  return useQuery<CaseRead>({
    queryKey: caseQueryKeys.case(caseId ?? "none"),
    queryFn: ({ signal }) => getCase(caseId!, signal),
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

export function useUploadCaseDocument(caseId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      if (!caseId) throw new Error("Case ID is required for upload.");
      return uploadCaseDocument(caseId, file);
    },
    onSuccess: async () => {
      if (!caseId) return;
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(caseId) }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.sources(caseId) }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId), exact: true }),
      ]);
    },
  });
}

export function useStartCaseAnalysis(caseId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: CaseAnalysisCreate) => {
      if (!caseId) throw new Error("Case ID is required to start analysis.");
      return startCaseAnalysis(caseId, request);
    },
    onSuccess: async (result: CaseAnalysisResultRead) => {
      if (!caseId) return;
      // The analysis is finished when this resolves, so its result is the truth.
      queryClient.setQueryData(caseQueryKeys.analysis(caseId), result);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId), exact: true }),
        queryClient.refetchQueries({ queryKey: caseQueryKeys.chat(caseId), exact: true }),
      ]);
    },
  });
}

export function useCaseMutations() {
  const queryClient = useQueryClient();

  const upsertCase = useCallback(
    (caseRecord: CaseRead) => {
      queryClient.setQueryData<CaseRead[]>(caseQueryKeys.cases(), (current) =>
        sortCases([
          {
            ...current?.find((item) => item.id === caseRecord.id),
            ...caseRecord,
          },
          ...(current ?? []).filter((item) => item.id !== caseRecord.id),
        ]),
      );
    },
    [queryClient],
  );

  const createMutation = useMutation({
    mutationFn: () => createCase(),
    onSuccess: upsertCase,
  });
  const updateMutation = useMutation({
    mutationFn: ({ caseId, title }: { caseId: string; title: string }) => updateCase(caseId, title),
    onSuccess: upsertCase,
  });
  const deleteMutation = useMutation({
    mutationFn: (caseId: string) => deleteCase(caseId),
    onSuccess: (_deleted, deletedCaseId) => {
      queryClient.setQueryData<CaseRead[]>(caseQueryKeys.cases(), (current) =>
        (current ?? []).filter((item) => item.id !== deletedCaseId),
      );
      // Explicitly removes the entire case subtree (case, chat, documents, sources, analysis)
      queryClient.removeQueries({ queryKey: caseQueryKeys.case(deletedCaseId) });
    },
  });

  return { createMutation, updateMutation, deleteMutation, upsertCase };
}
