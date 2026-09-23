import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listCaseDocuments,
  listCaseSources,
  uploadCaseDocument,
  type CaseDocumentRead,
  type CaseSourceRead,
} from "@/lib/api";
import { caseQueryKeys } from "@/lib/queryKeys";

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

export function useUploadCaseDocument(caseId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      if (!caseId) throw new Error("Case ID is required for upload.");
      return uploadCaseDocument(caseId, file);
    },
    onSuccess: () => {
      if (!caseId) return;
      void Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.documents(caseId) }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.sources(caseId) }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId), exact: true }),
      ]);
    },
  });
}
