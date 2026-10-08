"use client";

import { useParams } from "next/navigation";
import { CaseSourcesView } from "@/features/sources/CaseSourcesView";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { EmptyState } from "@/components/EmptyState";
import { toUserFacingError } from "@/lib/userFacingError";
import { useCase } from "@/features/cases/queries";
import { useAnalysisAvailability } from "@/features/analysis/queries";
import { useRunCaseAnalysis } from "@/features/analysis/useRunCaseAnalysis";
import { useCaseSourceActions } from "@/features/sources/useCaseSourceActions";
import { useCaseSourceRows } from "@/features/sources/useCaseSourceRows";

export function SourcesPage() {
  const { caseId } = useParams<{ caseId: string }>();

  const caseQuery = useCase(caseId);
  const { isUpdating, isWaitingForFollowup, canAnalyze } = useAnalysisAvailability(caseId);
  const runAnalysis = useRunCaseAnalysis(caseId);

  const sourceRows = useCaseSourceRows(caseId);
  const actions = useCaseSourceActions({ caseId });

  if (sourceRows.isError) {
    return (
      <EmptyState
        title="Sources could not be loaded"
        description="The case sources could not be read. Nothing was changed."
        className="flex-1 justify-center px-6 py-16"
      >
        <button type="button" onClick={sourceRows.refetch} className="btn-primary mt-5">
          Try again
        </button>
      </EmptyState>
    );
  }

  return (
    <>
      <CaseSourcesView
        caseId={caseId}
        sources={sourceRows.sources}
        followups={sourceRows.followups}
        isUploading={actions.isUploadingDocument}
        uploadingFilename={actions.uploadingFilename}
        isAddingNarrative={actions.isAddingNarrative}
        isRetryingDocument={actions.isRetryingDocument}
        onUploadDocument={(file) => void actions.uploadDocument(file)}
        onRetryDocument={actions.retryDocument}
        onAddNarrative={actions.addNarrative}
        analysis={
          caseQuery.data
            ? {
                freshness: caseQuery.data.analysis_freshness,
                isRunning: isUpdating,
                isWaitingForFollowup,
                canAnalyze,
                onAnalyze: runAnalysis,
              }
            : undefined
        }
      />
      <MeaningfulErrorModal
        isOpen={actions.actionError !== null}
        error={actions.actionError !== null ? toUserFacingError(actions.actionError) : null}
        onClose={actions.clearActionError}
      />
    </>
  );
}
