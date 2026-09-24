"use client";

import { useCallback, useRef, useState } from "react";
import { Icon } from "@/components/icons";
import { useDismiss } from "@/lib/useDismiss";
import { formatBytes, formatDate } from "@/lib/format";
import type { CaseDocumentRead, CaseSourceRead } from "@/lib/api";
import type { SourcesAnalysis } from "./CaseSourcesView";

export type RailItem =
  | { id: string; kind: "file"; document: CaseDocumentRead; source: CaseSourceRead | null }
  | { id: string; kind: "narrative" | "followup_answer"; source: CaseSourceRead };

interface RailGroup {
  label: string;
  items: RailItem[];
}

export function railGroups(documents: CaseDocumentRead[], sources: CaseSourceRead[]): RailGroup[] {
  const written = (kind: "narrative" | "followup_answer") =>
    sources
      .filter((source) => source.source_kind === kind)
      .map((source): RailItem => ({ id: source.id, kind, source }));
  const read = new Map(
    sources
      .filter((source) => source.source_kind === "document")
      .map((source) => [source.document_id, source]),
  );

  return [
    {
      label: "Files",
      items: documents.map((document): RailItem => ({
        id: document.id,
        kind: "file",
        document,
        source: read.get(document.id) ?? null,
      })),
    },
    { label: "Case narrative", items: written("narrative") },
    { label: "Follow-up answers", items: written("followup_answer") },
  ].filter((group) => group.items.length > 0);
}

export function itemTitle(item: RailItem): string {
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
  onOpenNarrative: () => void;
  onPickFile: () => void;
  analysis?: SourcesAnalysis;
}

export function SourceRail({
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
          Sources changed since the last analysis
        </p>
      )}
      <button
        type="button"
        onClick={onAnalyze}
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
    const state = item.source ? null : "Pending";
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
            File
          </button>
        </div>
      )}
    </div>
  );
}
