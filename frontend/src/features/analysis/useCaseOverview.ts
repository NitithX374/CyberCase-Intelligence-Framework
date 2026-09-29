import { useMemo } from "react";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { useCaseSources } from "@/features/sources/queries";
import { buildCaseOverview } from "./overview";

export function useCaseOverview(caseId: string) {
  const analysisQuery = useCaseAnalysis(caseId);
  const sourcesQuery = useCaseSources(caseId);
  const analysisResult = analysisQuery.data ?? null;
  const sources = sourcesQuery.data ?? null;
  const overview = useMemo(
    () => buildCaseOverview(analysisResult, sources),
    [analysisResult, sources],
  );
  return { analysisQuery, sourcesQuery, analysisResult, sources, overview };
}
