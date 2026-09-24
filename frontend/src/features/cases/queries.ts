import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { createCase, deleteCase, getCase, listCases, updateCase, type CaseRead } from "@/lib/api";
import { caseQueryKeys } from "@/lib/queryKeys";

function sortCases(cases: CaseRead[]): CaseRead[] {
  return [...cases].sort(
    (left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at),
  );
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
      queryClient.removeQueries({ queryKey: caseQueryKeys.case(deletedCaseId) });
    },
  });

  return { createMutation, updateMutation, deleteMutation, upsertCase };
}
