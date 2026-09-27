import { useMutation, useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";
import { listCaseSources, uploadCaseDocument } from "./api";
import type { CaseSourceRead } from "@/lib/api/types";
import { caseQueryKeys } from "@/lib/queryKeys";

export function useCaseSources(caseId: string | null) {
  return useQuery<CaseSourceRead[]>({
    queryKey: caseQueryKeys.sources(caseId ?? "none"),
    queryFn: ({ signal }) => listCaseSources(caseId!, signal),
    enabled: caseId !== null,
    retry: false,
  });
}

export function refreshAfterSourceChange(queryClient: QueryClient, caseId: string) {
  return Promise.all([
    queryClient.invalidateQueries({ queryKey: caseQueryKeys.sources(caseId), exact: true }),
    queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId), exact: true }),
    queryClient.invalidateQueries({ queryKey: caseQueryKeys.analysis(caseId), exact: true }),
  ]);
}

export function useUploadCaseDocument(caseId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      if (!caseId) throw new Error("Case ID is required for upload.");
      return uploadCaseDocument(caseId, file);
    },
    onSettled: () => {
      if (caseId) void refreshAfterSourceChange(queryClient, caseId);
    },
  });
}
