"use client";

import { useMemo, useState } from "react";

import { MaterialPreviewViewport, type MaterialPreviewMode } from "./MaterialPreviewViewport";
import { MaterialSourceRail } from "./MaterialSourceRail";
import type { CaseDocumentRead, EvidenceSourceRead } from "@/lib/api";

interface CaseMaterialsViewProps {
  caseId: string;
  documents: CaseDocumentRead[];
  evidence: EvidenceSourceRead[];
  isUploading: boolean;
  admittingExtractionId: string | null;
  onUploadDocument: (file: File) => void;
  onAdmitExtraction: (documentId: string, extractionId: string) => void;
  onOpenChat?: () => void;
  onOpenIntake?: () => void;
}

export function CaseMaterialsView({
  caseId,
  documents,
  evidence,
  isUploading,
  admittingExtractionId,
  onUploadDocument,
  onAdmitExtraction,
  onOpenChat,
  onOpenIntake,
}: CaseMaterialsViewProps) {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<MaterialPreviewMode>("original");

  const admittedExtractionIds = useMemo(
    () => new Set(evidence.flatMap((source) => source.revisions?.flatMap((revision) => revision.extraction_id ? [revision.extraction_id] : []) ?? [])),
    [evidence],
  );
  const selectedDocument = documents.find((document) => document.id === selectedDocumentId) ?? documents[0] ?? null;
  const selectedExtraction = selectedDocument
    ? [...(selectedDocument.extractions ?? [])].sort((left, right) => right.revision - left.revision)[0] ?? null
    : null;
  const selectedExtractionIsAdmitted = selectedExtraction ? admittedExtractionIds.has(selectedExtraction.id) : false;

  return (
    <div
      id="workspace-materials-panel"
      role="tabpanel"
      aria-label="Case Materials"
      className="flex min-h-0 flex-1 flex-col overflow-hidden bg-surface"
    >
      <div className="flex min-h-0 flex-1 flex-col md:flex-row">
        <MaterialSourceRail
          documents={documents}
          selectedDocumentId={selectedDocument?.id ?? null}
          admittedExtractionIds={admittedExtractionIds}
          isUploading={isUploading}
          onSelectDocument={setSelectedDocumentId}
          onUploadDocument={onUploadDocument}
        />

        <MaterialPreviewViewport
          caseId={caseId}
          document={selectedDocument}
          extraction={selectedExtraction}
          mode={previewMode}
          isAdmitted={selectedExtractionIsAdmitted}
          isAdmitting={selectedExtraction?.id === admittingExtractionId}
          onModeChange={setPreviewMode}
          onAdmitExtraction={onAdmitExtraction}
          onOpenChat={onOpenChat}
          onOpenIntake={onOpenIntake}
        />
      </div>
    </div>
  );
}
