import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { createCase, deleteCase, getCase, listCases, updateCase } from "./api";
import type { CaseRead } from "@/lib/api/types";
import { caseQueryKeys } from "@/lib/queryKeys";

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

export function useCaseMutations() {
  const queryClient = useQueryClient();

  const upsertCase = useCallback(
    (caseRecord: CaseRead) => {
      queryClient.setQueryData<CaseRead[]>(caseQueryKeys.cases(), (current) => [
        caseRecord,
        ...(current ?? []).filter((item) => item.id !== caseRecord.id),
      ]);
      queryClient.setQueryData(caseQueryKeys.case(caseRecord.id), caseRecord);
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
      queryClient.removeQueries({ queryKey: caseQueryKeys.case(deletedCaseId) });
    },
  });

  return { createMutation, updateMutation, deleteMutation };
}
