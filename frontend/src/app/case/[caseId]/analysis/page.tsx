"use client";

import { useParams, useRouter } from "next/navigation";
import { CaseOverviewView } from "@/features/analysis/CaseOverviewView";
import { TechnicalContextView } from "@/features/technical-context/TechnicalContextView";
import { CaseReportView } from "@/features/reports/CaseReportView";
import { useCase } from "@/features/cases/queries";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { useCaseSources } from "@/features/sources/queries";
import { casePath } from "@/features/workspace/routes";

/**
 * Everything the case analysis produced, on one page.
 *
 * Findings, the ATT&CK context they were read against, and the report built
 * from them used to be three routes. They are three readings of one analysis,
 * and splitting them meant the reader had to know which tab held the part they
 * wanted before they could look for it.
 */
export default function CaseAnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = (params?.caseId as string) ?? null;

  const caseQuery = useCase(caseId);
  const analysisQuery = useCaseAnalysis(caseId);
  const sourcesQuery = useCaseSources(caseId);

  const activeCase = caseQuery.data ?? null;
  const analysisResult = analysisQuery.data ?? null;
  const openSources = () => {
    if (caseId) router.push(casePath(caseId, "sources"));
  };

  // Until there is an analysis the overview's own empty state is the whole
  // page: ATT&CK context and a report are both readings of an analysis.
  return (
    <>
      <CaseOverviewView caseId={caseId} />
      {analysisResult && (
        <TechnicalContextView
          analysisResult={analysisResult}
          sources={sourcesQuery.data ?? null}
          onOpenSources={openSources}
          onNavigateToSource={openSources}
        />
      )}
      {caseId && analysisResult && (
        <CaseReportView
          key={`${caseId}:${analysisResult.id}`}
          caseId={caseId}
          caseTitle={activeCase?.title || "New case"}
          analysisResult={analysisResult}
        />
      )}
    </>
  );
}
