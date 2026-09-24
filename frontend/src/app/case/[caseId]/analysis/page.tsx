"use client";

import { useParams } from "next/navigation";
import { CaseOverviewView } from "@/features/analysis/CaseOverviewView";
import { TechnicalContextView } from "@/features/technical-context/TechnicalContextView";
import { CaseReportView } from "@/features/reports/CaseReportView";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { useCaseSourceRows } from "@/features/sources/useCaseSourceRows";

export default function CaseAnalysisPage() {
  const { caseId } = useParams<{ caseId: string }>();

  const analysisResult = useCaseAnalysis(caseId).data ?? null;
  const {
    rows: sources,
    isLoading: sourcesLoading,
    isError: sourcesError,
  } = useCaseSourceRows(caseId);

  return (
    <>
      <CaseOverviewView caseId={caseId} />
      {analysisResult && (
        <TechnicalContextView
          analysisResult={analysisResult}
          sources={sourcesLoading || sourcesError ? null : sources}
        />
      )}
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
