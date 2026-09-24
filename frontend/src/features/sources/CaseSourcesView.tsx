"use client";

import { useMemo, useRef, useState } from "react";
import { Icon } from "@/components/icons";
import { EmptyState } from "@/components/EmptyState";
import type { CaseDocumentRead, CaseSourceRead } from "@/lib/api";
import { NarrativeDialog } from "./NarrativeDialog";
import { SourceRail, railGroups } from "./SourceRail";
import { SourceViewport, type PreviewMode } from "./SourceViewport";

export interface NarrativeSubmission {
  text: string;
}

export interface SourcesAnalysis {
  freshness: "missing" | "current" | "stale";
  isRunning: boolean;
  onAnalyze: () => void;
}

interface CaseSourcesViewProps {
  caseId: string;
  documents: CaseDocumentRead[];
  sources: CaseSourceRead[];
  isUploading: boolean;
  uploadingFilename?: string | null;
  isAddingNarrative: boolean;
  onUploadDocument: (file: File) => void;
  onAddNarrative: (submission: NarrativeSubmission) => Promise<boolean>;
  analysis?: SourcesAnalysis;
}

const ACCEPTED_FILES = ".pdf,.docx,.png,.jpg,.jpeg";

export function CaseSourcesView({
  caseId,
  documents,
  sources,
  isUploading,
  uploadingFilename,
  isAddingNarrative,
  onUploadDocument,
  onAddNarrative,
  analysis,
}: CaseSourcesViewProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<PreviewMode>("original");
  const [isNarrativeOpen, setIsNarrativeOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const groups = useMemo(() => railGroups(documents, sources), [documents, sources]);
  const items = useMemo(() => groups.flatMap((group) => group.items), [groups]);
  const selected = items.find((item) => item.id === selectedId) ?? items[0] ?? null;
  const isEmpty = items.length === 0 && !isUploading;

  const handleAddNarrative = async (submission: NarrativeSubmission) => {
    const added = await onAddNarrative(submission);
    if (added) setIsNarrativeOpen(false);
  };
  const openNarrative = () => setIsNarrativeOpen(true);
  const pickFile = () => fileInputRef.current?.click();

  return (
    <div
      id="workspace-sources-panel"
      role="tabpanel"
      aria-label="Case sources"
      className="flex min-h-0 flex-1 flex-col overflow-hidden bg-surface"
    >
      {isEmpty ? (
        <EmptySources onOpenNarrative={openNarrative} onPickFile={pickFile} />
      ) : (
        <div className="flex min-h-0 flex-1 flex-col md:flex-row">
          <SourceRail
            groups={groups}
            selectedId={selected?.id ?? null}
            isUploading={isUploading}
            uploadingFilename={uploadingFilename}
            onSelect={setSelectedId}
            onOpenNarrative={openNarrative}
            onPickFile={pickFile}
            analysis={analysis}
          />

          <SourceViewport
            caseId={caseId}
            item={selected}
            mode={previewMode}
            onModeChange={setPreviewMode}
          />
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_FILES}
        aria-label="Add file"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onUploadDocument(file);
          event.currentTarget.value = "";
        }}
        className="sr-only"
        tabIndex={-1}
      />

      <NarrativeDialog
        isOpen={isNarrativeOpen}
        isSaving={isAddingNarrative}
        onCancel={() => setIsNarrativeOpen(false)}
        onSubmit={(submission) => void handleAddNarrative(submission)}
      />
    </div>
  );
}

function EmptySources({
  onOpenNarrative,
  onPickFile,
}: {
  onOpenNarrative: () => void;
  onPickFile: () => void;
}) {
  return (
    <EmptyState
      title="No sources yet"
      description="Start with what happened, or a document."
      className="flex-1 justify-center px-6 py-16"
    >
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        <button type="button" onClick={onOpenNarrative} className="btn-primary">
          <Icon name="edit" className="h-4 w-4" />
          Write narrative
        </button>
        <button type="button" onClick={onPickFile} className="btn-secondary">
          <Icon name="upload" className="h-4 w-4" />
          Upload file
        </button>
      </div>
      <p className="mt-3 text-xs text-ink-muted">PDF, DOCX, PNG or JPG</p>
    </EmptyState>
  );
}
