import { ANALYSIS_REQUEST_TIMEOUT_MS, caseUrl, http } from "@/lib/api/http";
import type { AnalysisStepRead, CaseAnalysisResultRead } from "@/lib/api/types";

export async function startCaseAnalysis(caseId: string): Promise<AnalysisStepRead> {
  return (
    await http.post<AnalysisStepRead>(
      caseUrl(caseId, "analysis"),
      {},
      { timeout: ANALYSIS_REQUEST_TIMEOUT_MS },
    )
  ).data;
}

export async function getCaseAnalysis(
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseAnalysisResultRead | null> {
  return (await http.get<CaseAnalysisResultRead | null>(caseUrl(caseId, "analysis"), { signal }))
    .data;
}
