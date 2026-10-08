"use client";

import { useCallback, useRef, useState } from "react";
import { Icon } from "@/components/icons";
import { useDismiss } from "@/lib/useDismiss";
import { formatBytes, formatDate } from "@/lib/format";
import type { CaseSourceRead } from "@/lib/api/types";
import type { SourcesAnalysis } from "./CaseSourcesView";
import type { FollowupAnswer } from "@/features/citations/types";

export type RailItem =
  | { id: string; kind: "file"; documentId: string; source: CaseSourceRead }
  | { id: string; kind: "narrative"; source: CaseSourceRead }
  | { id: string; kind: "followup_answer"; followup: FollowupAnswer };

interface RailGroup {
  label: string;
  items: RailItem[];
}

export function railGroups(sources: CaseSourceRead[], followups: FollowupAnswer[]): RailGroup[] {
  return [
    {
      label: "Files",
      items: sources.flatMap((source): RailItem[] =>
        source.source_kind === "document" && source.document_id
          ? [{ id: source.id, kind: "file", documentId: source.document_id, source }]
          : [],
      ),
    },
    {
      label: "Case narrative",
      items: sources
        .filter((source) => source.source_kind === "narrative")
        .map((source): RailItem => ({ id: source.id, kind: "narrative", source })),
    },
    {
      label: "Follow-up answers",
      items: followups.map((followup): RailItem => ({
        id: followup.qaId,
        kind: "followup_answer",
        followup,
      })),
    },
  ].filter((group) => group.items.length > 0);
}

export function itemTitle(item: RailItem): string {
  if (item.kind === "file") return item.source.filename ?? "Untitled file";
  if (item.kind === "followup_answer")
    return firstLine(item.followup.question || item.followup.answer);
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
          isAnalysing={analysis?.isRunning ?? false}
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
  const { freshness, isRunning, isWaitingForFollowup, canAnalyze, onAnalyze } = analysis;
  if (freshness === "current" && !isRunning && !isWaitingForFollowup) return null;
  const isStale = freshness === "stale";

  return (
    <div className="shrink-0 border-t border-line p-3">
      {isWaitingForFollowup && !isRunning && (
        <p className="mb-2.5 px-1 text-xs leading-5 text-ink-secondary">
          Answer the follow-up question in Ask to continue automatically.
        </p>
      )}
      {isStale && !isRunning && (
        <p className="mb-2.5 flex items-center gap-2 px-1 text-xs text-ink-secondary">
          Sources changed since the last analysis
        </p>
      )}
      <button
        type="button"
        onClick={onAnalyze}
        disabled={!canAnalyze || isRunning || isUploading}
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
  const detail =
    item.kind === "file"
      ? formatBytes(item.source.size_bytes ?? 0)
      : item.kind === "followup_answer"
        ? firstLine(item.followup.answer)
        : formatDate(item.source.created_at, "day");

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
        <span className="mt-0.5 block truncate text-xs text-ink-muted">{detail}</span>
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
  isAnalysing,
  onOpenNarrative,
  onPickFile,
}: {
  isUploading: boolean;
  isAnalysing: boolean;
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
        disabled={isUploading || isAnalysing}
        onClick={() => setIsOpen((open) => !open)}
        title={isAnalysing ? "Wait for the analysis to finish" : undefined}
        className="btn-primary h-8 px-3"
      >
        <Icon name="plus" className="h-4 w-4" />
        Add source
      </button>

      {isOpen && (
        <div
          role="menu"
          className="absolute right-0 top-9 z-20 w-52 overflow-hidden rounded-xl border border-line bg-surface p-1.5 shadow-lg shadow-black/5"
        >
          <button
            type="button"
            role="menuitem"
            disabled={isAnalysing}
            onClick={() => {
              setIsOpen(false);
              onOpenNarrative();
            }}
            className="flex h-9 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-[13px] text-ink hover:bg-surface-hover disabled:text-ink-disabled disabled:hover:bg-transparent"
          >
            Case narrative
          </button>
          <button
            type="button"
            role="menuitem"
            disabled={isAnalysing}
            onClick={() => {
              setIsOpen(false);
              onPickFile();
            }}
            className="flex h-9 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-[13px] text-ink hover:bg-surface-hover disabled:text-ink-disabled disabled:hover:bg-transparent"
          >
            File
          </button>
        </div>
      )}
    </div>
  );
}
