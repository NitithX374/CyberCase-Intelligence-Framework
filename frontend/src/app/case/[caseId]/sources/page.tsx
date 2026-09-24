"use client";

import { useParams } from "next/navigation";
import { CaseSourcesView } from "@/features/sources/CaseSourcesView";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { EmptyState } from "@/components/EmptyState";
import { toUserFacingError } from "@/lib/userFacingError";
import { useCase } from "@/features/cases/queries";
import { useCaseDocuments } from "@/features/sources/queries";
import { useIsAnalysisUpdating } from "@/features/analysis/queries";
import { useRunCaseAnalysis } from "@/features/analysis/useRunCaseAnalysis";
import { useCaseSourceActions } from "@/features/sources/useCaseSourceActions";
import { useCaseSourceRows } from "@/features/sources/useCaseSourceRows";

export default function SourcesPage() {
  const { caseId } = useParams<{ caseId: string }>();

  const caseQuery = useCase(caseId);
  const documentsQuery = useCaseDocuments(caseId);
  const isAnalyzing = useIsAnalysisUpdating(caseId);
  const runAnalysis = useRunCaseAnalysis(caseId);

  const sourceRows = useCaseSourceRows(caseId);
  const actions = useCaseSourceActions({ caseId });

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
                isRunning: isAnalyzing,
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
