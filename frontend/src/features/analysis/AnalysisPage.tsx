"use client";

import { useParams } from "next/navigation";
import { CaseOverviewView } from "@/features/analysis/CaseOverviewView";
import { TechnicalContextView } from "@/features/technical-context/TechnicalContextView";
import { CaseReportView } from "@/features/reports/CaseReportView";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { useCaseSources } from "@/features/sources/queries";

export function AnalysisPage() {
  const { caseId } = useParams<{ caseId: string }>();

  const analysisResult = useCaseAnalysis(caseId).data ?? null;
  const sources = useCaseSources(caseId).data ?? null;

  return (
    <>
      <CaseOverviewView caseId={caseId} />
      {analysisResult && <TechnicalContextView analysisResult={analysisResult} sources={sources} />}
      {analysisResult && (
        <CaseReportView
          key={`${caseId}:${analysisResult.id}`}
          caseId={caseId}
          analysisResult={analysisResult}
        />
      )}
    </>
  );
}
