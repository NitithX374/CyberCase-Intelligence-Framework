"use client";

import { useParams, useRouter } from "next/navigation";
import { CaseReportView } from "@/components/report/CaseReportView";
import { caseProcessingStatus, useCase, useCaseAnalysis, useCaseRunState } from "@/hooks/useCaseQueries";
import { casePath } from "@/lib/workspaceRoutes";

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const caseQuery = useCase(caseId ?? null);
  const activeCase = caseQuery.data ?? null;

  const analysisQuery = useCaseAnalysis(caseId ?? null);

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunState(caseId ?? null, runId);
  const runStatus = runQuery.data?.status ?? caseProcessingStatus(activeCase);

  return (
    <CaseReportView
      key={`${caseId}:${analysisQuery.data?.id ?? "empty"}`}
      caseId={caseId}
      caseTitle={activeCase?.title || "New case"}
      analysisResult={analysisQuery.data ?? null}
      runStatus={runStatus}
      onOpenOverview={() => router.push(casePath(caseId, activeCase?.latest_analysis_result_id ? "overview" : "materials"))}
    />
  );
}
