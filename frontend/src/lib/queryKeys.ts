export const caseQueryKeys = {
  all: ["cases"] as const,
  cases: () => [...caseQueryKeys.all, "list"] as const,
  case: (caseId: string) => [...caseQueryKeys.all, caseId] as const,
  chat: (caseId: string) => [...caseQueryKeys.case(caseId), "chat"] as const,
  documents: (caseId: string) => [...caseQueryKeys.case(caseId), "documents"] as const,
  sources: (caseId: string) => [...caseQueryKeys.case(caseId), "sources"] as const,
  analysis: (caseId: string) => [...caseQueryKeys.case(caseId), "analysis"] as const,
  reports: (caseId: string) => [...caseQueryKeys.case(caseId), "reports"] as const,
  analysisRun: (caseId: string) => [...caseQueryKeys.case(caseId), "analysis", "run"] as const,
};
