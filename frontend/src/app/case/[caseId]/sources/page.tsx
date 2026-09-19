"use client";

import { useParams, useRouter } from "next/navigation";
import { CaseSourcesView } from "@/components/sources/CaseSourcesView";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/userFacingError";
import { useCaseDocuments, useCaseSources } from "@/hooks/useCaseQueries";
import { useCaseSourceActions } from "@/hooks/useCaseSourceActions";

export default function SourcesPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.caseId as string;

  const documentsQuery = useCaseDocuments(caseId ?? null);
  const sourcesQuery = useCaseSources(caseId ?? null);

  const sources = sourcesQuery.data ?? [];
  const actions = useCaseSourceActions({ caseId: caseId ?? null, sources, router });

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
      />
      <MeaningfulErrorModal
        isOpen={Boolean(actions.actionError)}
        error={actions.actionError ? toUserFacingError(actions.actionError) : null}
        onClose={actions.clearActionError}
      />
    </>
  );
}
