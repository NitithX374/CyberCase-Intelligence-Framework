export const caseQueryKeys = {
  all: ["cases"] as const,
  cases: () => [...caseQueryKeys.all, "list"] as const,
  case: (caseId: string) => [...caseQueryKeys.all, caseId] as const,
  chat: (caseId: string) => [...caseQueryKeys.case(caseId), "chat"] as const,
  documents: (caseId: string) => [...caseQueryKeys.case(caseId), "documents"] as const,
  sources: (caseId: string) => [...caseQueryKeys.case(caseId), "sources"] as const,
  analysis: (caseId: string) => [...caseQueryKeys.case(caseId), "analysis"] as const,
  reports: (caseId: string) => [...caseQueryKeys.case(caseId), "reports"] as const,
  // Not a query. A mutation key, so a running analysis can be found in the
  // mutation cache by the case it belongs to rather than by the component
  // that happened to start it.
  analysisRun: (caseId: string) => [...caseQueryKeys.case(caseId), "analysis", "run"] as const,
};
