"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode } from "react";
import { Icon } from "@/components/common/icons";
import {
  fetchCaseDocumentContent,
  type CaseDocumentRead,
  type CaseSourceRead,
  type DocumentExtractionRead,
} from "@/lib/api";

export interface NarrativeSubmission {
  title?: string;
  text: string;
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
}

export function CaseSourcesView({
  caseId,
  documents,
  sources,
  isUploading,
  uploadingFilename,
  isAddingNarrative,
  onUploadDocument,
  onAddNarrative,
}: CaseSourcesViewProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<PreviewMode>("original");
  const [isNarrativeOpen, setIsNarrativeOpen] = useState(false);

  const groups = useMemo(() => railGroups(documents, sources), [documents, sources]);
  const items = useMemo(() => groups.flatMap((group) => group.items), [groups]);
  const selected = items.find((item) => item.id === selectedId) ?? items[0] ?? null;

  const handleAddNarrative = async (submission: NarrativeSubmission) => {
    const added = await onAddNarrative(submission);
    if (added) setIsNarrativeOpen(false);
  };

  return (
    <div
      id="workspace-sources-panel"
      role="tabpanel"
      aria-label="Case sources"
      className="flex min-h-0 flex-1 flex-col overflow-hidden bg-surface"
    >
      <div className="flex min-h-0 flex-1 flex-col md:flex-row">
        <SourceRail
          groups={groups}
          selectedId={selected?.id ?? null}
          isUploading={isUploading}
          uploadingFilename={uploadingFilename}
          onSelect={setSelectedId}
          onUploadDocument={onUploadDocument}
          onOpenNarrative={() => setIsNarrativeOpen(true)}
        />

        <SourceViewport
          caseId={caseId}
          item={selected}
          mode={previewMode}
          onModeChange={setPreviewMode}
          onOpenNarrative={() => setIsNarrativeOpen(true)}
        />
      </div>

      <NarrativeDialog
        isOpen={isNarrativeOpen}
        isSaving={isAddingNarrative}
        onCancel={() => setIsNarrativeOpen(false)}
        onSubmit={(submission) => void handleAddNarrative(submission)}
      />
    </div>
  );
}

/** A source the case knows: an uploaded file, a narrative, or a follow-up answer. */
type RailItem =
  | { id: string; kind: "file"; document: CaseDocumentRead }
  | { id: string; kind: "narrative" | "followup_answer"; source: CaseSourceRead };

interface RailGroup {
  label: string;
  items: RailItem[];
}

function railGroups(documents: CaseDocumentRead[], sources: CaseSourceRead[]): RailGroup[] {
  const written = (kind: "narrative" | "followup_answer") =>
    sources
      .filter((source) => source.source_kind === kind)
      .map((source): RailItem => ({ id: source.id, kind, source }));

  return [
    {
      label: "Files",
      items: documents.map((document): RailItem => ({ id: document.id, kind: "file", document })),
    },
    { label: "Case narrative", items: written("narrative") },
    { label: "Follow-up answers", items: written("followup_answer") },
  ].filter((group) => group.items.length > 0);
}

function latestExtraction(document: CaseDocumentRead): DocumentExtractionRead | null {
  return (
    [...(document.extractions ?? [])].sort(
      (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
    )[0] ?? null
  );
}

function itemTitle(item: RailItem): string {
  if (item.kind === "file") return item.document.filename;
  return firstLine(item.source.exact_text);
}

function firstLine(text: string): string {
  const line = text.trim().split("\n")[0] ?? "";
  return line.length > 80 ? `${line.slice(0, 80)}…` : line || "Untitled source";
}

interface SourceRailProps {
  groups: RailGroup[];
  selectedId: string | null;
  isUploading: boolean;
  uploadingFilename?: string | null;
  onSelect: (id: string) => void;
  onUploadDocument: (file: File) => void;
  onOpenNarrative: () => void;
}

function SourceRail({
  groups,
  selectedId,
  isUploading,
  uploadingFilename,
  onSelect,
  onUploadDocument,
  onOpenNarrative,
}: SourceRailProps) {
  const total = groups.reduce((count, group) => count + group.items.length, 0);
  const shown = total + (isUploading ? 1 : 0);

  return (
    <aside className="flex max-h-72 w-full shrink-0 flex-col border-b border-line bg-sidebar md:max-h-none md:w-64 md:border-r md:border-b-0">
      <header className="flex min-h-12 items-center justify-between border-b border-line px-3">
        <div>
          <h2 className="text-xs font-semibold text-ink">Sources</h2>
          <p className="text-[10px] text-ink-muted">
            {shown} source{shown === 1 ? "" : "s"}
          </p>
        </div>
        <AddSourceMenu
          isUploading={isUploading}
          onUploadDocument={onUploadDocument}
          onOpenNarrative={onOpenNarrative}
        />
      </header>

      <div className="min-h-0 flex-1 overflow-auto p-2">
        {total === 0 && !isUploading ? (
          <p className="px-2 py-4 text-[11px] leading-5 text-ink-muted">
            Nothing yet. Add a case narrative or a file.
          </p>
        ) : (
          <div className="space-y-4">
            {isUploading && <UploadingItem filename={uploadingFilename} />}
            {groups.map((group) => (
              <section key={group.label}>
                <h3 className="px-2 pb-1 text-[10px] font-semibold tracking-wide text-ink-muted uppercase">
                  {group.label}
                </h3>
                <ul className="space-y-0.5">
                  {group.items.map((item) => (
                    <li key={item.id}>
                      <RailButton
                        item={item}
                        selected={item.id === selectedId}
                        onSelect={() => onSelect(item.id)}
                      />
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

function RailButton({
  item,
  selected,
  onSelect,
}: {
  item: RailItem;
  selected: boolean;
  onSelect: () => void;
}) {
  let detail: string;
  if (item.kind === "file") {
    const extraction = latestExtraction(item.document);
    const state = item.document.archived_at ? "Archived" : extraction ? "Received" : "Pending";
    detail = `${formatBytes(item.document.size_bytes)} · ${state}`;
  } else {
    detail = new Date(item.source.created_at).toLocaleDateString();
  }

  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
      className={`w-full rounded-md px-2.5 py-2 text-left outline-none focus-visible:ring-2 focus-visible:ring-accent ${selected ? "bg-accent-soft text-ink" : "text-ink-secondary hover:bg-surface-hover hover:text-ink"}`}
    >
      <span className="flex items-start gap-2">
        <Icon
          name={item.kind === "file" ? "sources" : "list"}
          className="mt-0.5 h-3.5 w-3.5 shrink-0"
        />
        <span className="min-w-0 flex-1">
          <span className="block truncate text-xs font-medium">{itemTitle(item)}</span>
          <span className="mt-0.5 block text-[10px] text-ink-muted">{detail}</span>
        </span>
      </span>
    </button>
  );
}

function UploadingItem({ filename }: { filename?: string | null }) {
  return (
    <div
      aria-live="polite"
      className="rounded-md border border-dashed border-accent/60 bg-accent-soft px-2.5 py-2.5"
    >
      <span className="block truncate text-xs font-medium text-ink">
        {filename || "Uploading file…"}
      </span>
      <span className="mt-0.5 block text-[10px] text-accent">Extracting text…</span>
    </div>
  );
}

function AddSourceMenu({
  isUploading,
  onUploadDocument,
  onOpenNarrative,
}: {
  isUploading: boolean;
  onUploadDocument: (file: File) => void;
  onOpenNarrative: () => void;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const dismiss = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setIsOpen(false);
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsOpen(false);
    };
    document.addEventListener("mousedown", dismiss);
    document.addEventListener("keydown", escape);
    return () => {
      document.removeEventListener("mousedown", dismiss);
      document.removeEventListener("keydown", escape);
    };
  }, [isOpen]);

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={isOpen}
        disabled={isUploading}
        onClick={() => setIsOpen((open) => !open)}
        className="flex h-8 w-8 items-center justify-center rounded-md text-ink-secondary hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-wait disabled:opacity-50"
      >
        <Icon name="plus" className="h-4 w-4" />
        <span className="sr-only">Add source</span>
      </button>

      {isOpen && (
        <div
          role="menu"
          className="absolute right-0 top-9 z-20 w-48 overflow-hidden rounded-md border border-line bg-surface py-1 shadow-lg shadow-black/5"
        >
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setIsOpen(false);
              onOpenNarrative();
            }}
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs text-ink hover:bg-surface-hover"
          >
            <Icon name="list" className="h-3.5 w-3.5 text-ink-muted" />
            Case narrative
          </button>
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setIsOpen(false);
              fileInputRef.current?.click();
            }}
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs text-ink hover:bg-surface-hover"
          >
            <Icon name="sources" className="h-3.5 w-3.5 text-ink-muted" />
            File
          </button>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.png,.jpg,.jpeg"
        aria-label="Add file"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onUploadDocument(file);
          event.currentTarget.value = "";
        }}
        className="sr-only"
      />
    </div>
  );
}

function NarrativeDialog({
  isOpen,
  isSaving,
  onCancel,
  onSubmit,
}: {
  isOpen: boolean;
  isSaving: boolean;
  onCancel: () => void;
  onSubmit: (submission: NarrativeSubmission) => void;
}) {
  const dialogRef = useRef<HTMLDialogElement | null>(null);
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");

  useEffect(() => {
    const element = dialogRef.current;
    if (!element) return;
    if (isOpen && !element.open) {
      setTitle("");
      setText("");
      if (typeof element.showModal === "function") element.showModal();
      else element.open = true;
    } else if (!isOpen && element.open) {
      if (typeof element.close === "function") element.close();
      else element.open = false;
    }
  }, [isOpen]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!text.trim() || isSaving) return;
    onSubmit({ title: title.trim() || undefined, text: text.trim() });
  };

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="case-narrative-title"
      onCancel={(event) => {
        event.preventDefault();
        if (!isSaving) onCancel();
      }}
      className="m-auto w-[min(40rem,calc(100vw-2rem))] rounded-lg border border-line bg-surface p-6 text-ink shadow-xl shadow-black/10 backdrop:bg-primary/35"
    >
      <form onSubmit={handleSubmit}>
        <h2 id="case-narrative-title" className="text-base font-semibold tracking-tight">
          Case narrative
        </h2>
        <p className="mt-1 text-xs text-ink-secondary">
          Describe what happened, who was involved, and the dates available. The narrative becomes a
          case source.
        </p>

        <label
          htmlFor="case-narrative-name"
          className="mt-5 block text-xs font-medium text-ink-secondary"
        >
          Case title <span className="text-ink-muted">(optional)</span>
        </label>
        <input
          id="case-narrative-name"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          disabled={isSaving}
          placeholder="A short name for this case"
          className="mt-1 w-full border-b border-line bg-transparent px-0 py-2 text-sm text-ink outline-none placeholder:text-ink-muted focus:border-accent disabled:text-ink-disabled"
        />

        <label
          htmlFor="case-narrative-text"
          className="mt-4 block text-xs font-medium text-ink-secondary"
        >
          Narrative
        </label>
        <textarea
          id="case-narrative-text"
          rows={8}
          value={text}
          onChange={(event) => setText(event.target.value)}
          disabled={isSaving}
          placeholder="Describe the incident and the material available."
          className="mt-1 block min-h-44 w-full resize-y rounded-md border border-line bg-surface p-3 text-sm leading-6 text-ink outline-none placeholder:text-ink-muted focus:border-accent focus:ring-1 focus:ring-accent disabled:bg-surface-nested"
        />

        <div className="mt-5 flex justify-end gap-2.5">
          <button
            type="button"
            disabled={isSaving}
            onClick={onCancel}
            className="h-9 rounded-md border border-line bg-surface px-3.5 text-xs font-semibold text-ink hover:bg-surface-hover disabled:cursor-not-allowed disabled:text-ink-disabled"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSaving || !text.trim()}
            className="h-9 rounded-md bg-primary px-3.5 text-xs font-semibold text-ivory hover:bg-charcoal-hover disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled"
          >
            {isSaving ? "Saving…" : "Add narrative"}
          </button>
        </div>
      </form>
    </dialog>
  );
}

type PreviewMode = "original" | "ocr" | "split";

interface SourceViewportProps {
  caseId: string;
  item: RailItem | null;
  mode: PreviewMode;
  onModeChange: (mode: PreviewMode) => void;
  onOpenNarrative: () => void;
}

function SourceViewport({
  caseId,
  item,
  mode,
  onModeChange,
  onOpenNarrative,
}: SourceViewportProps) {
  const extraction = item?.kind === "file" ? latestExtraction(item.document) : null;

  return (
    <section
      aria-label="Source preview"
      className="flex min-h-0 min-w-0 flex-1 flex-col bg-surface"
    >
      <header className="flex min-h-12 flex-wrap items-center gap-3 border-b border-line px-3 sm:px-4">
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-xs font-semibold text-ink">
            {item ? itemTitle(item) : "Select a source"}
          </h2>
          {item?.kind === "file" && extraction && (
            <p className="truncate text-[10px] text-ink-muted">{extraction.provider}</p>
          )}
          {item && item.kind !== "file" && (
            <p className="truncate text-[10px] text-ink-muted">
              {item.kind === "followup_answer" ? "Follow-up answer" : "Case narrative"}
            </p>
          )}
        </div>

        {item?.kind === "file" && (
          <div
            role="tablist"
            aria-label="Source representation"
            className="flex h-8 items-end gap-4"
          >
            <PreviewTab selected={mode === "original"} onClick={() => onModeChange("original")}>
              Original File
            </PreviewTab>
            <PreviewTab selected={mode === "ocr"} onClick={() => onModeChange("ocr")}>
              System OCR
            </PreviewTab>
            <PreviewTab selected={mode === "split"} onClick={() => onModeChange("split")}>
              Side by Side
            </PreviewTab>
          </div>
        )}
      </header>

      <div className="min-h-0 flex-1 bg-canvas">
        {!item ? (
          <EmptyPreview onOpenNarrative={onOpenNarrative} />
        ) : item.kind !== "file" ? (
          <TextSourcePreview source={item.source} />
        ) : mode === "original" ? (
          <OriginalFilePreview caseId={caseId} document={item.document} />
        ) : mode === "ocr" ? (
          <SystemOcrPreview extraction={extraction} />
        ) : (
          <div className="flex h-full min-h-0 flex-col divide-y divide-line lg:flex-row lg:divide-x lg:divide-y-0">
            <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">
              <OriginalFilePreview caseId={caseId} document={item.document} />
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

function PreviewTab({
  selected,
  onClick,
  children,
}: {
  selected: boolean;
  onClick: () => void;
  children: string;
}) {
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

function TextSourcePreview({ source }: { source: CaseSourceRead }) {
  return (
    <div className="h-full overflow-auto p-4 sm:p-6">
      <article className="mx-auto max-w-3xl rounded-md border border-line bg-surface px-5 py-6 shadow-sm sm:px-8 sm:py-8">
        <p className="mb-4 border-b border-line pb-2.5 text-[11px] text-ink-muted">
          Added {new Date(source.created_at).toLocaleString()}
        </p>
        <p className="whitespace-pre-wrap break-words text-sm leading-7 text-ink">
          {source.exact_text}
        </p>
      </article>
    </div>
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

  useEffect(
    () => () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    },
    [objectUrl],
  );

  if (query.isLoading) return <ViewportMessage title="Loading original file…" />;
  if (query.error || !objectUrl) {
    return (
      <ViewportMessage title="Original file could not be loaded.">
        <button
          type="button"
          onClick={() => void query.refetch()}
          className="mt-4 text-xs font-semibold text-accent underline underline-offset-4"
        >
          Try again
        </button>
      </ViewportMessage>
    );
  }

  const canEmbed =
    document.mime_type === "application/pdf" || document.mime_type.startsWith("image/");
  if (!canEmbed) {
    return (
      <ViewportMessage title="This file type opens outside the preview.">
        <a
          href={objectUrl}
          download={document.filename}
          className="mt-4 inline-flex h-9 items-center rounded-md bg-primary px-4 text-xs font-semibold text-ivory"
        >
          Open original file
        </a>
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
  const rawPages = Array.isArray(provenance?.pages)
    ? (provenance.pages as ExtractionPageItem[])
    : [];

  if (rawPages.length === 0) {
    return [{ pageNumber: 1, text: extraction.extracted_text }];
  }

  return rawPages.map((page, index) => ({
    pageNumber: typeof page.page_number === "number" ? page.page_number : index + 1,
    text:
      typeof page.text === "string"
        ? page.text
        : typeof page.merged_text === "string"
          ? page.merged_text
          : "",
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
                {extraction.warnings_json.length} warning
                {extraction.warnings_json.length === 1 ? "" : "s"}
              </span>
            )}
          </div>

          {pages.length > 1 && (
            <nav aria-label="Page navigation" className="flex flex-wrap items-center gap-1">
              <span className="mr-1 text-[10px] uppercase tracking-wider text-ink-muted">
                Jump to:
              </span>
              {pages.map((p) => (
                <button
                  key={p.pageNumber}
                  type="button"
                  onClick={() => {
                    document
                      .getElementById(`ocr-page-${p.pageNumber}`)
                      ?.scrollIntoView({ behavior: "smooth", block: "start" });
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

function EmptyPreview({ onOpenNarrative }: { onOpenNarrative: () => void }) {
  return (
    <ViewportMessage title="This case has no sources yet.">
      <button
        type="button"
        onClick={onOpenNarrative}
        className="mt-4 text-xs font-semibold text-accent underline underline-offset-4"
      >
        Add a case narrative
      </button>
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

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
