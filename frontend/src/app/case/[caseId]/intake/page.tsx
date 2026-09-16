"use client";

import { useParams, useRouter } from "next/navigation";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/user-facing-error";
import {
  useCase,
  useCaseAnalysis,
  useCaseDocuments,
  useCaseEvidence,
  useCaseMutations,
  useCaseRunPolling,
} from "@/hooks/useCaseQueries";
import { useCaseIntakeActions } from "@/hooks/useCaseIntakeActions";
import { casePath } from "@/lib/workspaceRoutes";

export default function IntakePage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const caseQuery = useCase(caseId ?? null);
  const { upsertCase, updateMutation } = useCaseMutations();
  const activeCase = caseQuery.data ?? null;

  const documentsQuery = useCaseDocuments(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);
  const analysisQuery = useCaseAnalysis(caseId ?? null);

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(caseId ?? null, runId);

  const actions = useCaseIntakeActions({
    activeCaseId: caseId,
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
        onSubmitCase={actions.submitCase}
        onUploadDocument={(file) => void actions.uploadDocument(file)}
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
