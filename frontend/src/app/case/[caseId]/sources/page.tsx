"use client";

import { useParams } from "next/navigation";
import { CaseSourcesView } from "@/components/sources/CaseSourcesView";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/userFacingError";
import {
  useCase,
  useCaseDocuments,
  useCaseSources,
  useIsCaseAnalysisRunning,
} from "@/hooks/useCaseQueries";
import { useCaseChatMessages } from "@/hooks/useCaseChat";
import { useCaseSourceActions } from "@/hooks/useCaseSourceActions";
import { mergeCaseSourceRows } from "@/lib/caseOverview/followupSources";
import { useWorkspaceActivity } from "@/components/layout/WorkspaceActivityContext";

export default function SourcesPage() {
  const params = useParams();
  const caseId = params?.caseId as string;

  const caseQuery = useCase(caseId ?? null);
  const documentsQuery = useCaseDocuments(caseId ?? null);
  const sourcesQuery = useCaseSources(caseId ?? null);
  const chatQuery = useCaseChatMessages({ caseId: caseId ?? null });
  const isAnalysisRunning = useIsCaseAnalysisRunning(caseId ?? null);
  const { isFollowupPending, runAnalysis } = useWorkspaceActivity();

  const caseSources = sourcesQuery.data ?? [];
  const sources = mergeCaseSourceRows(caseSources, chatQuery.data?.messages ?? []);
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
