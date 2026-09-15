"use client";

import { useParams, useRouter } from "next/navigation";
import { useMemo } from "react";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/user-facing-error";
import {
  useCaseAnalysis,
  useCaseDocuments,
  useCaseEvidence,
  useCaseMutations,
  useCases,
} from "@/hooks/useCaseQueries";
import { useCaseRunPolling } from "@/hooks/useCaseRunPolling";
import { useCaseWorkspaceActions } from "@/hooks/useCaseWorkspaceActions";
import { casePath } from "@/features/chat/routing/workspaceRoutes";

export default function IntakePage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const casesQuery = useCases();
  const { upsertCase, updateMutation } = useCaseMutations();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCase = cases.find((c) => c.id === caseId) ?? null;

  const documentsQuery = useCaseDocuments(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);
  const analysisQuery = useCaseAnalysis(caseId ?? null);

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(caseId ?? null, runId, caseId);

  const actions = useCaseWorkspaceActions({
    activeCaseId: caseId,
    activeCase,
    upsertCase,
    updateCase: updateMutation.mutateAsync,
    router,
  });

  const isCaseDataLoading =
    documentsQuery.isLoading || evidenceQuery.isLoading || analysisQuery.isLoading;

  return (
    <>
      <CaseIntakeView
        caseId={caseId}
        documents={documentsQuery.data ?? []}
        evidence={evidenceQuery.data ?? []}
        analysisResult={analysisQuery.data ?? null}
        run={runQuery.data ?? null}
        isSubmitting={actions.isSubmitting}
        isCaseDataLoading={isCaseDataLoading}
        error={actions.actionError}
        isUploadingDocument={actions.isUploadingDocument}
        admittingExtractionId={actions.admittingExtractionId}
        onSubmitCase={actions.submitCase}
        onUploadDocument={(file) => void actions.uploadDocument(file)}
        onAdmitExtraction={(docId, extId) => void actions.admitExtraction(docId, extId)}
        onOpenOverview={() => router.push(casePath(caseId, "overview"))}
        onOpenMaterials={() => router.push(casePath(caseId, "materials"))}
      />
      <MeaningfulErrorModal
        isOpen={Boolean(actions.actionError)}
        error={actions.actionError ? toUserFacingError(actions.actionError) : null}
        onClose={actions.clearActionError}
      />
    </>
  );
}
