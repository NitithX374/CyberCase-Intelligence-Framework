"use client";

import { useParams, useRouter } from "next/navigation";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import {
  useCase,
  useCaseAnalysis,
  useCaseEvidence,
  useCaseFollowUps,
  useCaseRunPolling,
  useStartCaseAnalysis,
} from "@/hooks/useCaseQueries";
import { casePath } from "@/lib/workspaceRoutes";
import { detectResponseLanguage } from "@/lib/api";

export default function OverviewPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const caseQuery = useCase(caseId ?? null);
  const activeCase = caseQuery.data ?? null;

  const analysisQuery = useCaseAnalysis(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);
  const followupsQuery = useCaseFollowUps(caseId ?? null);

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(caseId ?? null, runId);
  const runStatus =
    runQuery.data?.status ??
    (activeCase?.processing_status === "queued" ||
    activeCase?.processing_status === "running" ||
    activeCase?.processing_status === "failed"
      ? activeCase.processing_status
      : null);

  const startAnalysisMutation = useStartCaseAnalysis(caseId ?? null);

  const handleRunAnalysis = async () => {
    if (!caseId || startAnalysisMutation.isPending) return;
    try {
      await startAnalysisMutation.mutateAsync({
        idempotency_key: globalThis.crypto.randomUUID(),
        response_language: detectResponseLanguage(
          evidenceQuery.data?.map((source) => source.exact_text).join("\n") ?? "",
        ),
        expected_evidence_revision: activeCase?.evidence_revision ?? 0,
      });
    } catch {
      // Handled by run state / error modals
    }
  };

  return (
    <CaseOverviewView
      caseId={caseId}
      caseTitle={activeCase?.title || "New case"}
      chatStatus={activeCase?.status ?? "idle"}
      analysisResult={analysisQuery.data ?? null}
      evidenceSources={evidenceQuery.data ?? []}
      runStatus={runStatus}
      run={runQuery.data ?? null}
      followups={followupsQuery.data ?? []}
      analysisLoading={analysisQuery.isLoading}
      evidenceLoading={evidenceQuery.isLoading}
      onOpenReport={() => router.push(casePath(caseId, "report"))}
      onOpenIntake={() => router.push(casePath(caseId, "intake"))}
      onOpenMaterials={() => router.push(casePath(caseId, "materials"))}
      onNavigateToSource={() => router.push(casePath(caseId, "materials"))}
      onRunAnalysis={() => void handleRunAnalysis()}
    />
  );
}
