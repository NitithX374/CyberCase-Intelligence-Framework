"use client";

import { useParams, useRouter } from "next/navigation";
import { useMemo } from "react";
import { CaseReportView } from "@/components/report/CaseReportView";
import { useCaseAnalysis, useCases } from "@/hooks/useCaseQueries";
import { useCaseRunPolling } from "@/hooks/useCaseRunPolling";
import { casePath } from "@/features/chat/routing/workspaceRoutes";

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const casesQuery = useCases();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCase = cases.find((c) => c.id === caseId) ?? null;

  const analysisQuery = useCaseAnalysis(caseId ?? null);

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(caseId ?? null, runId, activeCase?.chat_thread_id);
  const runStatus =
    runQuery.data?.status ??
    (activeCase?.processing_status === "queued" ||
    activeCase?.processing_status === "running" ||
    activeCase?.processing_status === "failed"
      ? activeCase.processing_status
      : null);

  return (
    <CaseReportView
      key={`${caseId}:${analysisQuery.data?.id ?? "empty"}`}
      caseId={caseId}
      caseTitle={activeCase?.title || "New case"}
      analysisResult={analysisQuery.data ?? null}
      runStatus={runStatus}
      onOpenChat={() => {}}
      onOpenOverview={() => router.push(casePath(caseId, "overview"))}
    />
  );
}
