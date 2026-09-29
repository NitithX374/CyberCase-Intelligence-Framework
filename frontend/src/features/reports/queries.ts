import { useQuery } from "@tanstack/react-query";
import { caseQueryKeys } from "@/lib/queryKeys";
import { listCaseReports } from "./api";

export function useCaseReports(caseId: string) {
  return useQuery({
    queryKey: caseQueryKeys.reports(caseId),
    queryFn: ({ signal }) => listCaseReports(caseId, signal),
    retry: false,
  });
}
