"use client";

import { useParams, useRouter } from "next/navigation";
import { useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import {
  useCaseAnalysis,
  useCaseEvidence,
  useCaseFollowUps,
  useCases,
  caseQueryKeys,
  useCaseRunPolling,
} from "@/hooks/useCaseQueries";
import { casePath } from "@/features/chat/routing/workspaceRoutes";
import { detectResponseLanguage, startCaseAnalysis } from "@/lib/api";

export default function OverviewPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const caseId = params?.caseId as string;

  const casesQuery = useCases();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCase = cases.find((c) => c.id === caseId) ?? null;

  const analysisQuery = useCaseAnalysis(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);
  const followupsQuery = useCaseFollowUps(caseId ?? null);

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(caseId ?? null, runId, caseId);
  const runStatus =
    runQuery.data?.status ??
    (activeCase?.processing_status === "queued" ||
    activeCase?.processing_status === "running" ||
    activeCase?.processing_status === "failed"
      ? activeCase.processing_status
      : null);

  const handleRunAnalysis = async () => {
    if (!caseId) return;
    try {
      const accepted = await startCaseAnalysis(caseId, {
        idempotency_key: globalThis.crypto.randomUUID(),
        response_language: detectResponseLanguage(
          evidenceQuery.data?.map((source) => source.exact_text).join("\n") ?? "",
        ),
        expected_evidence_revision: activeCase?.evidence_revision ?? 0,
      });
      queryClient.setQueryData(caseQueryKeys.run(caseId, accepted.run.id), accepted.run);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.analysis(caseId) }),
      ]);
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
      onOpenTechnicalContext={() => router.push(casePath(caseId, "technical-context"))}
      onNavigateToSource={() => router.push(casePath(caseId, "materials"))}
      onRunAnalysis={() => void handleRunAnalysis()}
    />
  );
}
