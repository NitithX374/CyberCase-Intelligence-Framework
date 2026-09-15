export const chatQueryKeys = {
  all: ["chat"] as const,
  cases: () => [...chatQueryKeys.all, "cases"] as const,
  case: (caseId: string) => [...chatQueryKeys.cases(), caseId] as const,
  detail: (caseId: string | null) =>
    [...chatQueryKeys.case(caseId ?? "none"), "detail"] as const,
};

