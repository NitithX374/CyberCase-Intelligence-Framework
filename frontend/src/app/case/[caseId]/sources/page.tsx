"use client";

import { useParams } from "next/navigation";
import { CaseSourcesView } from "@/features/sources/CaseSourcesView";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
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

  const { rows: sources } = useCaseSourceRows(caseId ?? null);
  const actions = useCaseSourceActions({ caseId: caseId ?? null });

  return (
    <>
      <CaseSourcesView
        caseId={caseId}
        documents={documentsQuery.data ?? []}
        sources={sources}
        isUploading={actions.isUploadingDocument}
        uploadingFilename={actions.uploadingFilename}
        isAddingNarrative={actions.isAddingNarrative}
        onUploadDocument={(file) => void actions.uploadDocument(file)}
        onAddNarrative={actions.addNarrative}
        // Until the case has loaded, whether it needs analyzing is unknown, and
        // guessing would flash the button at an up-to-date case.
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
        isOpen={Boolean(actions.actionError)}
        error={actions.actionError ? toUserFacingError(actions.actionError) : null}
        onClose={actions.clearActionError}
      />
    </>
  );
}
