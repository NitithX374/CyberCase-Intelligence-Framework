"use client";

import { useParams } from "next/navigation";
import { CaseSourcesView } from "@/features/sources/CaseSourcesView";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { EmptyState } from "@/components/EmptyState";
import { toUserFacingError } from "@/lib/userFacingError";
import { useCase } from "@/features/cases/queries";
import { useCaseDocuments } from "@/features/sources/queries";
import { useIsCaseAnalysisRunning } from "@/features/analysis/queries";
import { useCaseSourceActions } from "@/features/sources/useCaseSourceActions";
import { useCaseSourceRows } from "@/features/sources/useCaseSourceRows";
import { useWorkspaceActivity } from "@/features/workspace/WorkspaceActivityContext";

export default function SourcesPage() {
  const params = useParams();
  const caseId = params?.caseId as string;

  const caseQuery = useCase(caseId ?? null);
  const documentsQuery = useCaseDocuments(caseId ?? null);
  const isAnalysisRunning = useIsCaseAnalysisRunning(caseId ?? null);
  const { isFollowupPending, runAnalysis } = useWorkspaceActivity();

  const sourceRows = useCaseSourceRows(caseId ?? null);
  const actions = useCaseSourceActions({ caseId: caseId ?? null });

  if (documentsQuery.isLoadingError || sourceRows.isError) {
    return (
      <EmptyState
        title="Sources could not be loaded"
        description="The case sources could not be read. Nothing was changed."
        className="flex-1 justify-center px-6 py-16"
      >
        <button
          type="button"
          onClick={() => {
            if (documentsQuery.isLoadingError) void documentsQuery.refetch();
            if (sourceRows.isError) sourceRows.refetch();
          }}
          className="btn-primary mt-5"
        >
          Try again
        </button>
      </EmptyState>
    );
  }

  return (
    <>
      <CaseSourcesView
        caseId={caseId}
        documents={documentsQuery.data ?? []}
        sources={sourceRows.rows}
        isUploading={actions.isUploadingDocument}
        uploadingFilename={actions.uploadingFilename}
        isAddingNarrative={actions.isAddingNarrative}
        onUploadDocument={(file) => void actions.uploadDocument(file)}
        onAddNarrative={actions.addNarrative}
        analysis={
          caseQuery.data
            ? {
                freshness: caseQuery.data.analysis_freshness,
                isRunning: isAnalysisRunning || isFollowupPending,
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
