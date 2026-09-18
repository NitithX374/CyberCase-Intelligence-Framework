"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Icon } from "@/components/common/icons";
import { fetchCaseDocumentContent, type CaseDocumentRead, type DocumentExtractionRead } from "@/lib/api";

interface CaseMaterialsViewProps {
  caseId: string;
  documents: CaseDocumentRead[];
  isUploading: boolean;
  uploadingFilename?: string | null;
  uploadingFileSize?: number | null;
  onUploadDocument: (file: File) => void;
}

export function CaseMaterialsView({
  caseId,
  documents,
  isUploading,
  uploadingFilename,
  uploadingFileSize,
  onUploadDocument,
}: CaseMaterialsViewProps) {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<MaterialPreviewMode>("original");

  const selectedDocument = documents.find((document) => document.id === selectedDocumentId) ?? documents[0] ?? null;
  const selectedExtraction = selectedDocument
    ? [...(selectedDocument.extractions ?? [])].sort(
        (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
      )[0] ?? null
    : null;
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
          isUploading={isUploading}
          uploadingFilename={uploadingFilename}
          uploadingFileSize={uploadingFileSize}
          onSelectDocument={setSelectedDocumentId}
          onUploadDocument={onUploadDocument}
        />

        <MaterialPreviewViewport
          caseId={caseId}
          document={selectedDocument}
          extraction={selectedExtraction}
          mode={previewMode}
          onModeChange={setPreviewMode}
        />
      </div>
    </div>
  );
}

type MaterialPreviewMode = "original" | "ocr" | "split";

interface MaterialPreviewViewportProps {
  caseId: string;
  document: CaseDocumentRead | null;
  extraction: DocumentExtractionRead | null;
  mode: MaterialPreviewMode;
  onModeChange: (mode: MaterialPreviewMode) => void;
}

function MaterialPreviewViewport({
  caseId,
  document,
  extraction,
  mode,
  onModeChange,
}: MaterialPreviewViewportProps) {
  return (
    <section aria-label="Source preview" className="flex min-h-0 min-w-0 flex-1 flex-col bg-surface">
      <header className="flex min-h-12 flex-wrap items-center gap-3 border-b border-line px-3 sm:px-4">
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-xs font-semibold text-ink">{document?.filename ?? "Select a source"}</h2>
          {document && extraction && <p className="truncate text-[10px] text-ink-muted">{extraction.provider}</p>}
        </div>

        <div role="tablist" aria-label="Source representation" className="flex h-8 items-end gap-4">
          <PreviewTab selected={mode === "original"} onClick={() => onModeChange("original")}>Original File</PreviewTab>
          <PreviewTab selected={mode === "ocr"} onClick={() => onModeChange("ocr")}>System OCR</PreviewTab>
          <PreviewTab selected={mode === "split"} onClick={() => onModeChange("split")}>Side by Side</PreviewTab>
        </div>

      </header>

      <div className="min-h-0 flex-1 bg-canvas">
        {!document ? (
          <EmptyPreview />
        ) : mode === "original" ? (
          <OriginalFilePreview caseId={caseId} document={document} />
        ) : mode === "ocr" ? (
          <SystemOcrPreview extraction={extraction} />
        ) : (
          <div className="flex h-full min-h-0 flex-col divide-y divide-line lg:flex-row lg:divide-x lg:divide-y-0">
            <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">
              <OriginalFilePreview caseId={caseId} document={document} />
            </div>
            <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">
              <SystemOcrPreview extraction={extraction} />
            </div>
          </div>
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
      className={`h-full border-b-2 px-0.5 text-[11px] font-medium outline-none focus-visible:ring-2 focus-visible:ring-accent ${selected ? "border-accent text-accent" : "border-transparent text-ink-muted hover:text-ink"}`}
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

  return <iframe src={objectUrl} title={`Original file: ${document.filename}`} className="h-full min-h-[28rem] w-full border-0 bg-surface" />;
}

interface ExtractionPageItem {
  page_number?: number;
  text?: string;
  merged_text?: string;
  text_method?: string;
  verification_status?: string;
}

interface ExtractionPage {
  pageNumber: number;
  text: string;
  method?: string;
}

function getExtractionPages(extraction: DocumentExtractionRead): ExtractionPage[] {
  const provenance = extraction.provenance_json as Record<string, unknown> | undefined;
  const rawPages = Array.isArray(provenance?.pages) ? (provenance.pages as ExtractionPageItem[]) : [];

  if (rawPages.length === 0) {
    return [{ pageNumber: 1, text: extraction.extracted_text }];
  }

  return rawPages.map((page, index) => ({
    pageNumber: typeof page.page_number === "number" ? page.page_number : index + 1,
    text: typeof page.text === "string" ? page.text : typeof page.merged_text === "string" ? page.merged_text : "",
    method: typeof page.text_method === "string" ? page.text_method : undefined,
  }));
}

function SystemOcrPreview({ extraction }: { extraction: DocumentExtractionRead | null }) {
  const pages = useMemo(() => (extraction ? getExtractionPages(extraction) : []), [extraction]);

  if (!extraction) return <ViewportMessage title="No system extraction is available." />;

  return (
    <div role="tabpanel" aria-label="System OCR" className="h-full overflow-auto p-4 sm:p-6">
      <div className="mx-auto max-w-4xl space-y-4">
        <header className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 rounded-md border border-line bg-surface/95 px-4 py-2.5 backdrop-blur shadow-sm">
          <div className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-ink">System OCR</span>
            <span className="text-ink-muted">·</span>
            <span className="text-ink-secondary">{extraction.provider}</span>
            <span className="rounded bg-canvas px-2 py-0.5 text-[11px] font-medium text-ink-muted">
              {pages.length} {pages.length === 1 ? "page" : "pages"}
            </span>
            {extraction.warnings_json.length > 0 && (
              <span className="text-unresolved text-xs">
                {extraction.warnings_json.length} warning{extraction.warnings_json.length === 1 ? "" : "s"}
              </span>
            )}
          </div>

          {pages.length > 1 && (
            <nav aria-label="Page navigation" className="flex flex-wrap items-center gap-1">
              <span className="mr-1 text-[10px] uppercase tracking-wider text-ink-muted">Jump to:</span>
              {pages.map((p) => (
                <button
                  key={p.pageNumber}
                  type="button"
                  onClick={() => {
                    document.getElementById(`ocr-page-${p.pageNumber}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
                  }}
                  className="rounded border border-line bg-surface px-2 py-0.5 text-xs text-ink-secondary hover:border-accent hover:text-accent focus:outline-none focus:ring-1 focus:ring-accent"
                >
                  P.{p.pageNumber}
                </button>
              ))}
            </nav>
          )}
        </header>

        {pages.map((page) => (
          <article
            key={page.pageNumber}
            id={`ocr-page-${page.pageNumber}`}
            className="scroll-mt-14 rounded-md border border-line bg-surface px-5 py-6 shadow-sm sm:px-8 sm:py-8"
          >
            <div className="mb-4 flex items-center justify-between border-b border-line pb-2.5">
              <div className="flex items-center gap-2">
                <span className="rounded bg-accent-soft px-2.5 py-0.5 text-xs font-bold text-accent">
                  Page {page.pageNumber}
                </span>
                {page.method && (
                  <span className="text-[11px] uppercase tracking-wider text-ink-muted">
                    {page.method}
                  </span>
                )}
              </div>
              <span className="text-[11px] text-ink-muted">
                {page.text.trim().length.toLocaleString()} chars
              </span>
            </div>

            {page.text.trim() ? (
              <p className="whitespace-pre-wrap break-words text-sm leading-7 text-ink">
                {page.text}
              </p>
            ) : (
              <p className="py-4 text-center text-xs italic text-ink-muted">
                (No text extracted on this page)
              </p>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}

function EmptyPreview() {
  return <ViewportMessage title="Add a source file using Add files above." />;
}

function ViewportMessage({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex h-full min-h-[24rem] flex-col items-center justify-center p-8 text-center">
      <p className="text-xs font-medium text-ink-secondary">{title}</p>
      {children}
    </div>
  );
}

interface MaterialSourceRailProps {
  documents: CaseDocumentRead[];
  selectedDocumentId: string | null;
  isUploading: boolean;
  uploadingFilename?: string | null;
  uploadingFileSize?: number | null;
  onSelectDocument: (documentId: string) => void;
  onUploadDocument: (file: File) => void;
}

function MaterialSourceRail({
  documents,
  selectedDocumentId,
  isUploading,
  uploadingFilename,
  uploadingFileSize,
  onSelectDocument,
  onUploadDocument,
}: MaterialSourceRailProps) {
  const totalCount = documents.length + (isUploading ? 1 : 0);

  return (
    <aside className="flex max-h-48 w-full shrink-0 flex-col border-b border-line bg-sidebar md:max-h-none md:w-60 md:border-r md:border-b-0">
      <header className="flex min-h-12 items-center justify-between border-b border-line px-3">
        <div>
          <h2 className="text-xs font-semibold text-ink">Sources</h2>
          <p className="text-[10px] text-ink-muted">{totalCount} file{totalCount === 1 ? "" : "s"}</p>
        </div>
        <label className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-md text-ink-secondary hover:bg-surface-hover hover:text-ink focus-within:ring-2 focus-within:ring-accent has-[:disabled]:cursor-wait has-[:disabled]:opacity-50">
          <Icon name="plus" className="h-4 w-4" />
          <span className="sr-only">{isUploading ? "Saving file" : "Add files"}</span>
          <input
            type="file"
            accept=".pdf,.docx,.png,.jpg,.jpeg"
            disabled={isUploading}
            aria-label="Add files"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onUploadDocument(file);
              event.currentTarget.value = "";
            }}
            className="sr-only"
          />
        </label>
      </header>

      <div className="min-h-0 overflow-auto p-2">
        {documents.length === 0 && !isUploading ? (
          <p className="px-2 py-4 text-[11px] leading-5 text-ink-muted">No source files yet.</p>
        ) : (
          <ul className="space-y-1">
            {isUploading && (
              <li aria-live="polite">
                <div className="w-full rounded-md border border-dashed border-accent/60 bg-accent-soft/60 px-2.5 py-2.5 text-left shadow-xs">
                  <span className="flex items-start gap-2">
                    <span className="relative mt-0.5 flex h-3.5 w-3.5 shrink-0 items-center justify-center">
                      <Icon name="materials" className="h-3.5 w-3.5 text-accent" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-xs font-semibold text-ink">
                        {uploadingFilename || "Uploading document…"}
                      </span>
                      <span className="mt-1 flex items-center gap-1.5 text-[10px] text-ink-muted">
                        {typeof uploadingFileSize === "number" && (
                          <>
                            <span>{formatBytes(uploadingFileSize)}</span>
                            <span aria-hidden="true">·</span>
                          </>
                        )}
                        <span className="inline-flex items-center gap-1 font-medium text-accent">
                          <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent" />
                          Pending extraction…
                        </span>
                      </span>
                    </span>
                  </span>
                </div>
              </li>
            )}
            {documents.map((document) => {
              const extraction = [...(document.extractions ?? [])].sort(
                (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
              )[0];
              const selected = document.id === selectedDocumentId;
              return (
                <li key={document.id}>
                  <button
                    type="button"
                    aria-pressed={selected}
                    onClick={() => onSelectDocument(document.id)}
                    className={`w-full rounded-md px-2.5 py-2.5 text-left outline-none focus-visible:ring-2 focus-visible:ring-accent ${selected ? "bg-accent-soft text-ink" : "text-ink-secondary hover:bg-surface-hover hover:text-ink"}`}
                  >
                    <span className="flex items-start gap-2">
                      <Icon name="materials" className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-xs font-semibold">{document.filename}</span>
                        <span className="mt-1 flex items-center gap-1.5 text-[10px] text-ink-muted">
                          <span>{formatBytes(document.size_bytes)}</span>
                          <span aria-hidden="true">·</span>
                          <span className={document.archived_at ? "text-ink-muted" : extraction ? "text-established" : ""}>{document.archived_at ? "Archived" : extraction ? "Received" : "Pending"}</span>
                        </span>
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </aside>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
