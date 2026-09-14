"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import type { ReactNode } from "react";

import type { CaseDocumentRead, DocumentExtractionRead } from "@/lib/api";
import { fetchCaseDocumentContent } from "@/lib/api";

export type MaterialPreviewMode = "original" | "ocr";

interface MaterialPreviewViewportProps {
  caseId: string;
  document: CaseDocumentRead | null;
  extraction: DocumentExtractionRead | null;
  mode: MaterialPreviewMode;
  isAdmitted: boolean;
  isAdmitting: boolean;
  onModeChange: (mode: MaterialPreviewMode) => void;
  onAdmitExtraction: (documentId: string, extractionId: string) => void;
  onOpenChat?: () => void;
  onOpenIntake?: () => void;
}

export function MaterialPreviewViewport({
  caseId,
  document,
  extraction,
  mode,
  isAdmitted,
  isAdmitting,
  onModeChange,
  onAdmitExtraction,
  onOpenChat,
  onOpenIntake,
}: MaterialPreviewViewportProps) {
  return (
    <section aria-label="Source preview" className="flex min-h-0 min-w-0 flex-1 flex-col bg-surface">
      <header className="flex min-h-12 flex-wrap items-center gap-3 border-b border-line px-3 sm:px-4">
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-xs font-semibold text-ink">{document?.filename ?? "Select a source"}</h2>
          {document && extraction && <p className="truncate text-[10px] text-ink-muted">Extraction revision {extraction.revision} · {extraction.provider}</p>}
        </div>

        <div role="tablist" aria-label="Source representation" className="flex h-8 items-end gap-4">
          <PreviewTab selected={mode === "original"} onClick={() => onModeChange("original")}>Original File</PreviewTab>
          <PreviewTab selected={mode === "ocr"} onClick={() => onModeChange("ocr")}>System OCR</PreviewTab>
        </div>

        <div className="flex items-center gap-2">
          {document && extraction && !isAdmitted && !document.archived_at && (
            <button
              type="button"
              disabled={isAdmitting}
              onClick={() => onAdmitExtraction(document.id, extraction.id)}
              className="h-8 rounded-md bg-primary px-3 text-[11px] font-semibold text-ivory hover:bg-charcoal-hover disabled:cursor-wait disabled:opacity-50"
            >
              {isAdmitting ? "Admitting…" : "Admit OCR"}
            </button>
          )}
          {onOpenChat && document && (
            <button type="button" onClick={onOpenChat} className="h-8 rounded-md border border-line px-3 text-[11px] font-semibold text-ink hover:bg-surface-hover">
              Ask
            </button>
          )}
        </div>
      </header>

      <div className="min-h-0 flex-1 bg-canvas">
        {!document ? (
          <EmptyPreview onOpenIntake={onOpenIntake} />
        ) : mode === "original" ? (
          <OriginalFilePreview caseId={caseId} document={document} />
        ) : (
          <SystemOcrPreview extraction={extraction} />
        )}
      </div>
    </section>
  );
}

function PreviewTab({ selected, onClick, children }: { selected: boolean; onClick: () => void; children: string }) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={selected}
      tabIndex={selected ? 0 : -1}
      onClick={onClick}
      className={`h-full border-b-2 px-0.5 text-[11px] font-medium outline-none focus-visible:ring-2 focus-visible:ring-accent ${
        selected ? "border-accent text-accent" : "border-transparent text-ink-muted hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}

function OriginalFilePreview({ caseId, document }: { caseId: string; document: CaseDocumentRead }) {
  const query = useQuery({
    queryKey: ["case-document-content", caseId, document.id],
    queryFn: ({ signal }) => fetchCaseDocumentContent(caseId, document.id, signal),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
  const objectUrl = useMemo(() => {
    if (!query.data || typeof URL.createObjectURL !== "function") return null;
    return URL.createObjectURL(query.data);
  }, [query.data]);

  useEffect(() => () => {
    if (objectUrl) URL.revokeObjectURL(objectUrl);
  }, [objectUrl]);

  if (query.isLoading) return <ViewportMessage title="Loading original file…" />;
  if (query.error || !objectUrl) {
    return (
      <ViewportMessage title="Original file could not be loaded.">
        <button type="button" onClick={() => void query.refetch()} className="mt-4 text-xs font-semibold text-accent underline underline-offset-4">Try again</button>
      </ViewportMessage>
    );
  }

  const canEmbed = document.mime_type === "application/pdf" || document.mime_type.startsWith("image/");
  if (!canEmbed) {
    return (
      <ViewportMessage title="This file type opens outside the preview.">
        <a href={objectUrl} download={document.filename} className="mt-4 inline-flex h-9 items-center rounded-md bg-primary px-4 text-xs font-semibold text-ivory">Open original file</a>
      </ViewportMessage>
    );
  }

  return (
    <iframe
      src={objectUrl}
      title={`Original file: ${document.filename}`}
      className="h-full min-h-[28rem] w-full border-0 bg-surface"
    />
  );
}

function SystemOcrPreview({ extraction }: { extraction: DocumentExtractionRead | null }) {
  if (!extraction) return <ViewportMessage title="No system extraction is available." />;
  return (
    <div role="tabpanel" aria-label="System OCR" className="h-full overflow-auto p-4 sm:p-6">
      <article className="mx-auto min-h-full max-w-4xl border border-line bg-surface px-5 py-6 sm:px-8 sm:py-8">
        <div className="mb-5 flex items-center justify-between border-b border-line pb-3 text-[10px] text-ink-muted">
          <span>System OCR · revision {extraction.revision}</span>
          {extraction.warnings_json.length > 0 && <span className="text-unresolved">{extraction.warnings_json.length} warning{extraction.warnings_json.length === 1 ? "" : "s"}</span>}
        </div>
        <p className="whitespace-pre-wrap break-words text-sm leading-7 text-ink">{extraction.extracted_text}</p>
      </article>
    </div>
  );
}

function EmptyPreview({ onOpenIntake }: { onOpenIntake?: () => void }) {
  return (
    <ViewportMessage title="Add a source file to begin reviewing materials.">
      {onOpenIntake && <button type="button" onClick={onOpenIntake} className="mt-4 text-xs font-semibold text-accent underline underline-offset-4">Go to Intake</button>}
    </ViewportMessage>
  );
}

function ViewportMessage({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex h-full min-h-[24rem] flex-col items-center justify-center p-8 text-center">
      <p className="text-xs font-medium text-ink-secondary">{title}</p>
      {children}
    </div>
  );
}
