import { caseUrl, http } from "@/lib/api/http";
import { postWithProgress, type StreamedStep } from "@/lib/api/stream";
import type { AnalysisStepRead, CaseAnalysisResultRead } from "@/lib/api/types";

export async function startCaseAnalysis(
  caseId: string,
  onStep: (step: StreamedStep) => void = () => undefined,
): Promise<AnalysisStepRead> {
  return postWithProgress<AnalysisStepRead>(caseUrl(caseId, "analysis"), {}, { onStep });
}

export async function getCaseAnalysis(
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseAnalysisResultRead | null> {
  return (await http.get<CaseAnalysisResultRead | null>(caseUrl(caseId, "analysis"), { signal }))
    .data;
}
