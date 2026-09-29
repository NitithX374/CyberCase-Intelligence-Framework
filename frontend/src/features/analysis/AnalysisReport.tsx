"use client";

import { useParams } from "next/navigation";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { CaseReportView } from "@/features/reports/CaseReportView";

export function AnalysisReport() {
  const { caseId } = useParams<{ caseId: string }>();
  const analysisResult = useCaseAnalysis(caseId).data ?? null;
  if (!analysisResult) return null;
  return (
    <CaseReportView
      key={`${caseId}:${analysisResult.id}`}
      caseId={caseId}
      analysisResult={analysisResult}
    />
  );
}
