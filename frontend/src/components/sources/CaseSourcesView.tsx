"use client";

import { useQuery } from "@tanstack/react-query";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import { Icon, type IconName } from "@/components/common/icons";
import { EmptyState } from "@/components/common/EmptyState";
import { useDismiss } from "@/hooks/useDismiss";
import { formatBytes, formatDate, plural } from "@/lib/format";
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

/** What the rail needs to offer the analysis as the next step. */
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

function itemIcon(item: RailItem): IconName {
  if (item.kind === "file") return "sources";
  return item.kind === "followup_answer" ? "reply" : "narrative";
}

function firstLine(text: string): string {
  const line = text.trim().split("\n")[0] ?? "";
  return line.length > 80 ? `${line.slice(0, 80)}…` : line || "Untitled source";
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
      icon="sources"
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

interface SourceRailProps {
  groups: RailGroup[];
  selectedId: string | null;
  isUploading: boolean;
  uploadingFilename?: string | null;
  onSelect: (id: string) => void;
  onOpenNarrative: () => void;
  onPickFile: () => void;
  analysis?: SourcesAnalysis;
}

function SourceRail({
  groups,
  selectedId,
  isUploading,
  uploadingFilename,
  onSelect,
  onOpenNarrative,
  onPickFile,
  analysis,
}: SourceRailProps) {
  const total = groups.reduce((count, group) => count + group.items.length, 0);
  const shown = total + (isUploading ? 1 : 0);

  return (
    <aside className="flex max-h-72 w-full shrink-0 flex-col border-b border-line bg-sidebar md:max-h-none md:w-72 md:border-r md:border-b-0">
      <header className="flex h-12 shrink-0 items-center justify-between pr-2 pl-4">
        <h2 className="flex items-baseline gap-2 text-[13px] font-semibold text-ink">
          Sources <span className="font-medium text-ink-muted">{shown}</span>
        </h2>
        <AddSourceMenu
          isUploading={isUploading}
          onOpenNarrative={onOpenNarrative}
          onPickFile={onPickFile}
        />
      </header>

      <div className="min-h-0 flex-1 space-y-5 overflow-auto px-2 pb-4">
        {isUploading && <UploadingItem filename={uploadingFilename} />}
        {groups.map((group) => (
          <section key={group.label}>
            <h3 className="px-2 pb-1 text-xs font-medium text-ink-muted">{group.label}</h3>
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

      {analysis && <AnalyzeFooter analysis={analysis} isUploading={isUploading} />}
    </aside>
  );
}

/**
 * The analysis, offered where it is the next step: once the case has sources
 * the analysis has not read. An up-to-date case has nothing to offer here, so
 * the rail ends at its last source; running it again is on Analysis.
 */
function AnalyzeFooter({
  analysis,
  isUploading,
}: {
  analysis: SourcesAnalysis;
  isUploading: boolean;
}) {
  const { freshness, isRunning, onAnalyze } = analysis;
  if (freshness === "current" && !isRunning) return null;
  const isStale = freshness === "stale";

  return (
    <div className="shrink-0 border-t border-line p-3">
      {isStale && !isRunning && (
        <p className="mb-2.5 flex items-center gap-2 px-1 text-xs text-ink-secondary">
          <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-unresolved" aria-hidden="true" />
          Sources changed since the last analysis
        </p>
      )}
      <button
        type="button"
        onClick={onAnalyze}
        // An analysis started mid-upload would read the case without the file.
        disabled={isRunning || isUploading}
        className="btn-primary w-full"
      >
        {isRunning && <Icon name="spinner" className="h-4 w-4" />}
        {isRunning ? "Analyzing…" : isStale ? "Analyze latest" : "Analyze"}
      </button>
    </div>
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
    const state = item.document.archived_at ? "Archived" : extraction ? null : "Pending";
    detail = [formatBytes(item.document.size_bytes), state].filter(Boolean).join(" · ");
  } else {
    detail = formatDate(item.source.created_at, "day");
  }

  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
      className={`flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2 text-left transition-colors ${
        selected
          ? "bg-surface text-ink shadow-xs ring-1 ring-line"
          : "text-ink-secondary hover:bg-surface-hover hover:text-ink"
      }`}
    >
      <Icon name={itemIcon(item)} className="mt-0.5 h-4 w-4 shrink-0 text-ink-muted" />
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[13px] font-medium">{itemTitle(item)}</span>
        <span className="mt-0.5 block text-xs text-ink-muted">{detail}</span>
      </span>
    </button>
  );
}

function UploadingItem({ filename }: { filename?: string | null }) {
  return (
    <div
      aria-live="polite"
      className="mx-0.5 flex items-start gap-2.5 rounded-lg border border-dashed border-line-strong bg-surface px-2.5 py-2"
    >
      <Icon name="spinner" className="mt-0.5 h-4 w-4 shrink-0 text-ink-muted" />
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[13px] font-medium text-ink">
          {filename || "Uploading file…"}
        </span>
        <span className="mt-0.5 block text-xs text-ink-muted">Extracting text…</span>
      </span>
    </div>
  );
}

function AddSourceMenu({
  isUploading,
  onOpenNarrative,
  onPickFile,
}: {
  isUploading: boolean;
  onOpenNarrative: () => void;
  onPickFile: () => void;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const close = useCallback(() => setIsOpen(false), []);
  useDismiss(containerRef, isOpen, close);

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={isOpen}
        disabled={isUploading}
        onClick={() => setIsOpen((open) => !open)}
        title="Add source"
        className="icon-btn disabled:cursor-wait"
      >
        <Icon name="plus" className="h-4 w-4" />
        <span className="sr-only">Add source</span>
      </button>

      {isOpen && (
        <div
          role="menu"
          className="absolute right-0 top-9 z-20 w-52 overflow-hidden rounded-xl border border-line bg-surface p-1.5 shadow-lg shadow-black/5"
        >
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setIsOpen(false);
              onOpenNarrative();
            }}
            className="flex h-9 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-[13px] text-ink hover:bg-surface-hover"
          >
            <Icon name="narrative" className="h-4 w-4 text-ink-muted" />
            Case narrative
          </button>
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setIsOpen(false);
              onPickFile();
            }}
            className="flex h-9 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-[13px] text-ink hover:bg-surface-hover"
          >
            <Icon name="upload" className="h-4 w-4 text-ink-muted" />
            File
          </button>
        </div>
      )}
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
      className="m-auto w-[min(38rem,calc(100vw-2rem))] rounded-2xl border border-line bg-surface p-6 text-ink shadow-2xl shadow-black/10 backdrop:bg-ink/30"
    >
      <form onSubmit={handleSubmit}>
        <h2 id="case-narrative-title" className="text-lg font-semibold tracking-tight">
          Case narrative
        </h2>

        <label
          htmlFor="case-narrative-name"
          className="mt-5 block text-[13px] font-medium text-ink"
        >
          Case title <span className="font-normal text-ink-muted">(optional)</span>
        </label>
        <input
          id="case-narrative-name"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          disabled={isSaving}
          placeholder="A short name for this case"
          className="mt-1.5 h-10 w-full rounded-lg border border-line-strong bg-surface px-3 text-[15px] text-ink outline-none placeholder:text-ink-muted focus:border-ink disabled:bg-surface-nested"
        />

        <label
          htmlFor="case-narrative-text"
          className="mt-4 block text-[13px] font-medium text-ink"
        >
          Narrative
        </label>
        <textarea
          id="case-narrative-text"
          rows={8}
          value={text}
          onChange={(event) => setText(event.target.value)}
          disabled={isSaving}
          placeholder="What happened, who was involved, and when."
          className="mt-1.5 block min-h-44 w-full resize-y rounded-lg border border-line-strong bg-surface p-3 text-[15px] leading-7 text-ink outline-none placeholder:text-ink-muted focus:border-ink disabled:bg-surface-nested"
        />

        <div className="mt-6 flex justify-end gap-2">
          <button type="button" disabled={isSaving} onClick={onCancel} className="btn-ghost">
            Cancel
          </button>
          <button type="submit" disabled={isSaving || !text.trim()} className="btn-primary">
            {isSaving && <Icon name="spinner" className="h-4 w-4" />}
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
}

function SourceViewport({ caseId, item, mode, onModeChange }: SourceViewportProps) {
  const extraction = item?.kind === "file" ? latestExtraction(item.document) : null;
  const pageCount = extraction ? getExtractionPages(extraction).length : 0;

  const subtitle = !item
    ? null
    : item.kind === "file"
      ? [fileKind(item.document), pageCount > 0 ? plural(pageCount, "page") : null]
          .filter(Boolean)
          .join(" · ")
      : item.kind === "followup_answer"
        ? "Follow-up answer"
        : "Case narrative";

  return (
    <section
      aria-label="Source preview"
      className="flex min-h-0 min-w-0 flex-1 flex-col bg-surface"
    >
      <header className="flex min-h-12 flex-wrap items-center gap-x-4 gap-y-2 border-b border-line px-4 py-2 sm:px-5">
        <div className="flex min-w-0 flex-1 basis-56 items-baseline gap-2.5">
          <h2 className="truncate text-[14px] font-semibold text-ink">
            {item ? itemTitle(item) : "Select a source"}
          </h2>
          {subtitle && <p className="shrink-0 text-xs text-ink-muted">{subtitle}</p>}
        </div>

        {item?.kind === "file" && (
          <div
            role="tablist"
            aria-label="Source representation"
            className="flex h-8 items-center gap-0.5 rounded-lg bg-surface-nested p-0.5"
          >
            <PreviewTab selected={mode === "original"} onClick={() => onModeChange("original")}>
              Original
            </PreviewTab>
            <PreviewTab selected={mode === "ocr"} onClick={() => onModeChange("ocr")}>
              Text
            </PreviewTab>
            <PreviewTab selected={mode === "split"} onClick={() => onModeChange("split")}>
              Side by side
            </PreviewTab>
          </div>
        )}
      </header>

      <div className="min-h-0 flex-1 bg-canvas">
        {!item ? (
          <ViewportMessage title="Select a source to read it." />
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
      className={`h-7 rounded-md px-2.5 text-[13px] font-medium transition-colors ${
        selected ? "bg-surface text-ink shadow-xs" : "text-ink-muted hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}

/** A page of text, set like paper on the canvas. */
function Paper({ label, children }: { label?: string; children: ReactNode }) {
  return (
    <section className="scroll-mt-4">
      {label && <h3 className="mb-2 px-1 text-xs font-medium text-ink-muted">{label}</h3>}
      <div className="rounded-xl border border-line bg-surface px-6 py-6 shadow-xs sm:px-10 sm:py-9">
        {children}
      </div>
    </section>
  );
}

function TextSourcePreview({ source }: { source: CaseSourceRead }) {
  return (
    <div className="h-full overflow-auto p-4 sm:p-8">
      <div className="mx-auto max-w-3xl">
        <Paper>
          <p className="whitespace-pre-wrap break-words text-[15px] leading-8 text-ink">
            {source.exact_text}
          </p>
        </Paper>
      </div>
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

  if (query.isLoading) {
    return (
      <div
        role="status"
        aria-label="Loading original file"
        className="flex h-full min-h-[24rem] items-center justify-center text-ink-muted"
      >
        <Icon name="spinner" className="h-6 w-6" />
      </div>
    );
  }
  if (query.error || !objectUrl) {
    return (
      <ViewportMessage title="The original file could not be loaded.">
        <button
          type="button"
          onClick={() => void query.refetch()}
          className="btn-secondary mt-4 h-8 px-3"
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
      <ViewportMessage title="This file type has no preview.">
        <a href={objectUrl} download={document.filename} className="btn-primary mt-4">
          <Icon name="download" className="h-4 w-4" />
          Download file
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

/** Enough pages that scrolling to one becomes a chore. */
const PAGE_JUMP_THRESHOLD = 4;

function SystemOcrPreview({ extraction }: { extraction: DocumentExtractionRead | null }) {
  const pages = useMemo(() => (extraction ? getExtractionPages(extraction) : []), [extraction]);

  if (!extraction) return <ViewportMessage title="No text was extracted from this file." />;

  const warnings = extraction.warnings_json.length;

  return (
    <div role="tabpanel" aria-label="Extracted text" className="h-full overflow-auto p-4 sm:p-8">
      <div className="mx-auto max-w-3xl space-y-6">
        {(warnings > 0 || pages.length >= PAGE_JUMP_THRESHOLD) && (
          <div className="flex flex-wrap items-center justify-between gap-3">
            {warnings > 0 ? (
              <p className="flex items-center gap-1.5 text-[13px] text-unresolved">
                <Icon name="alert" className="h-4 w-4" />
                {plural(warnings, "extraction warning")}
              </p>
            ) : (
              <span />
            )}
            {pages.length >= PAGE_JUMP_THRESHOLD && (
              <nav aria-label="Page navigation" className="flex flex-wrap items-center gap-0.5">
                {pages.map((page) => (
                  <button
                    key={page.pageNumber}
                    type="button"
                    aria-label={`Go to page ${page.pageNumber}`}
                    onClick={() => {
                      document
                        .getElementById(`ocr-page-${page.pageNumber}`)
                        ?.scrollIntoView({ behavior: "smooth", block: "start" });
                    }}
                    className="h-7 min-w-7 rounded-md px-1.5 text-xs font-medium text-ink-muted transition-colors hover:bg-surface hover:text-ink"
                  >
                    {page.pageNumber}
                  </button>
                ))}
              </nav>
            )}
          </div>
        )}

        {pages.map((page) => (
          <div key={page.pageNumber} id={`ocr-page-${page.pageNumber}`} className="scroll-mt-4">
            <Paper label={`Page ${page.pageNumber}`}>
              {page.text.trim() ? (
                <p className="whitespace-pre-wrap break-words text-[15px] leading-8 text-ink">
                  {page.text}
                </p>
              ) : (
                <p className="text-sm text-ink-muted">No text on this page.</p>
              )}
            </Paper>
          </div>
        ))}
      </div>
    </div>
  );
}

function ViewportMessage({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex h-full min-h-[24rem] flex-col items-center justify-center p-8 text-center">
      <p className="text-sm text-ink-muted">{title}</p>
      {children}
    </div>
  );
}

function fileKind(document: CaseDocumentRead): string {
  const extension = document.filename.split(".").pop()?.toUpperCase();
  if (document.mime_type === "application/pdf") return "PDF";
  if (document.mime_type.startsWith("image/")) return extension ?? "Image";
  return extension ?? "File";
}
