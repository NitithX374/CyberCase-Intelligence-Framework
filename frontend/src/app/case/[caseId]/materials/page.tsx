"use client";

import { useParams, useRouter } from "next/navigation";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import { CasePreparationPanel } from "@/components/materials/CasePreparationPanel";
import { useCaseIntakeActions } from "@/hooks/useCaseIntakeActions";
import {
  useCase,
  useCaseAnalysis,
  useCaseDocuments,
  useCaseEvidence,
  useCaseMutations,
} from "@/hooks/useCaseQueries";
import { toUserFacingError } from "@/lib/user-facing-error";

export default function MaterialsPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const caseQuery = useCase(caseId ?? null);
  const documentsQuery = useCaseDocuments(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);
  const analysisQuery = useCaseAnalysis(caseId ?? null);
  const { upsertCase, updateMutation } = useCaseMutations();
  const actions = useCaseIntakeActions({
    activeCaseId: caseId,
    upsertCase,
    updateCase: updateMutation.mutateAsync,
    router,
  });
  const isCaseDataLoading = caseQuery.isLoading || documentsQuery.isLoading || evidenceQuery.isLoading || analysisQuery.isLoading;

  return (
    <>
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-surface">
        <CasePreparationPanel
          caseId={caseId}
          evidence={evidenceQuery.data ?? []}
          caseStatus={caseQuery.data?.status ?? null}
          processingStatus={caseQuery.data?.processing_status ?? null}
          analysisResult={analysisQuery.data ?? null}
          isSubmitting={actions.isSubmitting}
          isCaseDataLoading={isCaseDataLoading}
          isUploading={actions.isUploadingDocument}
          error={actions.actionError}
          onSubmitCase={actions.submitCase}
        />
        <div className="min-h-[32rem] flex-1">
          <CaseMaterialsView
            caseId={caseId}
            documents={documentsQuery.data ?? []}
            isUploading={actions.isUploadingDocument}
            uploadingFilename={actions.uploadingFilename}
            onUploadDocument={(file) => void actions.uploadDocument(file)}
          />
        </div>
      </div>
      <MeaningfulErrorModal
        isOpen={Boolean(actions.actionError)}
        error={actions.actionError ? toUserFacingError(actions.actionError) : null}
        onClose={actions.clearActionError}
      />
    </>
  );
}
