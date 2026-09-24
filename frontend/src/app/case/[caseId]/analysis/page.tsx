"use client";

import { useParams, useRouter } from "next/navigation";
import { CaseOverviewView } from "@/features/analysis/CaseOverviewView";
import { TechnicalContextView } from "@/features/technical-context/TechnicalContextView";
import { CaseReportView } from "@/features/reports/CaseReportView";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { useCaseSourceRows } from "@/features/sources/useCaseSourceRows";
import { casePath } from "@/features/workspace/routes";

export default function CaseAnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = (params?.caseId as string) ?? null;

  const analysisQuery = useCaseAnalysis(caseId);
  const {
    rows: sources,
    isLoading: sourcesLoading,
    isError: sourcesError,
  } = useCaseSourceRows(caseId);

  const analysisResult = analysisQuery.data ?? null;
  const openSources = () => {
    if (caseId) router.push(casePath(caseId, "sources"));
  };

  return (
    <>
      <CaseOverviewView caseId={caseId} />
      {analysisResult && (
        <TechnicalContextView
          analysisResult={analysisResult}
          sources={sourcesLoading || sourcesError ? null : sources}
          onOpenSources={openSources}
        />
      )}
      {caseId && analysisResult && (
        <CaseReportView
          key={`${caseId}:${analysisResult.id}`}
          caseId={caseId}
          analysisResult={analysisResult}
        />
      )}
    </>
  );
}
