"use client";

import { Icon } from "@/components/icons";
import { formatBytes, formatDate } from "@/lib/format";
import type { CaseSourceRead } from "@/lib/api/types";
import type { SourcesAnalysis } from "./CaseSourcesView";
import type { FollowupAnswer } from "@/features/citations/types";
import { documentPages, fileKind, readByOcr } from "./sourcePresentation";

export type RailItem =
  | { id: string; kind: "file"; documentId: string; source: CaseSourceRead }
  | { id: string; kind: "narrative"; source: CaseSourceRead }
  | { id: string; kind: "followup_answer"; followup: FollowupAnswer };

interface RailGroup {
  label: string;
  items: RailItem[];
}

export function isTurnedOff(source: CaseSourceRead): boolean {
  return source.deactivated_at != null;
}

function currentReadings(sources: CaseSourceRead[]): CaseSourceRead[] {
  const newest = new Map<string, CaseSourceRead>();
  for (const source of sources) {
    if (!source.document_id) continue;
    const kept = newest.get(source.document_id);
    if (!kept || Date.parse(source.created_at) >= Date.parse(kept.created_at)) {
      newest.set(source.document_id, source);
    }
  }
  return sources.filter(
    (source) => !source.document_id || newest.get(source.document_id) === source,
  );
}

function sourceItems(sources: CaseSourceRead[], kind: "file" | "narrative"): RailItem[] {
  return sources.flatMap((source): RailItem[] => {
    if (kind === "file" && source.source_kind === "document" && source.document_id) {
      return [{ id: source.document_id, kind: "file", documentId: source.document_id, source }];
    }
    if (kind === "narrative" && source.source_kind === "narrative") {
      return [{ id: source.id, kind: "narrative", source }];
    }
    return [];
  });
}

export function railGroups(sources: CaseSourceRead[], followups: FollowupAnswer[]): RailGroup[] {
  const current = currentReadings(sources);
  return [
    { label: "Files", items: sourceItems(current, "file") },
    { label: "Case narrative", items: sourceItems(current, "narrative") },
    {
      label: "Your answers (not sources)",
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
  onSetSourceActive?: (sourceId: string, active: boolean) => Promise<void>;
  isSwitchingSource?: boolean;
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
  onSetSourceActive,
  isSwitchingSource = false,
  analysis,
}: SourceRailProps) {
  const total = groups.reduce((count, group) => count + group.items.length, 0);
  const shown = total + (isUploading ? 1 : 0);
  const isAnalysing = analysis?.isRunning ?? false;
  const switchable = groups.flatMap((group) =>
    group.items.flatMap((item) => (item.kind === "followup_answer" ? [] : [item.source])),
  );
  const usedCount = switchable.filter((source) => !isTurnedOff(source)).length;

  return (
    <aside className="sheet flex max-h-96 w-full shrink-0 flex-col overflow-hidden md:max-h-none md:w-[25rem]">
      <header className="shrink-0 space-y-3 border-b border-line px-5 pt-4 pb-4">
        <h2 className="flex items-center gap-2.5 text-lg font-semibold text-ink">
          <Icon name="sources" className="text-xl text-primary" />
          In this case <span className="count-pill">{shown}</span>
          {onSetSourceActive && switchable.length > 0 && (
            <span className="ml-auto text-sm font-normal text-ink-muted">
              {usedCount} of {switchable.length} used
            </span>
          )}
        </h2>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={isUploading || isAnalysing}
            onClick={onOpenNarrative}
            title={isAnalysing ? "Wait for the analysis to finish" : undefined}
            className="btn-primary"
          >
            <Icon name="edit" className="text-xl" />
            Add narrative
          </button>
          <button
            type="button"
            disabled={isUploading || isAnalysing}
            onClick={onPickFile}
            title={isAnalysing ? "Wait for the analysis to finish" : undefined}
            className="btn-secondary"
          >
            <Icon name="upload" className="text-xl" />
            Upload file
          </button>
        </div>
      </header>

      <div className="min-h-0 flex-1 space-y-5 overflow-auto px-3 pt-3 pb-4">
        {isUploading && <UploadingItem filename={uploadingFilename} />}
        {groups.map((group) => (
          <section key={group.label}>
            <h3 className="px-2 pb-1.5 text-xs font-semibold tracking-[0.08em] text-ink-muted uppercase">
              {group.label}
            </h3>
            <ul className="space-y-1">
              {group.items.map((item) => (
                <li
                  key={item.id}
                  className={`flex items-start gap-1 rounded-lg pl-2 ${
                    item.id === selectedId ? "bg-primary-wash ring-1 ring-primary-line" : ""
                  }`}
                >
                  {onSetSourceActive &&
                    (item.kind === "followup_answer" ? (
                      <span aria-hidden="true" className="w-8 shrink-0" />
                    ) : (
                      <SourceCheckbox
                        source={item.source}
                        title={itemTitle(item)}
                        isAnalysing={isAnalysing}
                        disabled={isSwitchingSource || isAnalysing}
                        onChange={onSetSourceActive}
                      />
                    ))}
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

      {onSetSourceActive && switchable.length > 0 && (
        <p className="shrink-0 border-t border-line px-5 py-3 text-sm text-ink-muted">
          Ticked sources go into the next analysis. Changing a tick makes the current analysis out
          of date.
        </p>
      )}
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
  const { freshness, isRunning, isWaitingForFollowup } = analysis;
  if (freshness === "current" && !isRunning && !isWaitingForFollowup) return null;
  const isStale = freshness === "stale";

  return (
    <div className="shrink-0 border-t border-line p-4" role="status">
      {isRunning ? (
        <p className="flex items-center gap-2 text-sm font-medium text-ink">
          <Icon name="spinner" className="text-xl" />
          Analyzing the sources…
        </p>
      ) : isWaitingForFollowup ? (
        <p className="text-sm text-ink-secondary">
          Waiting for your answer in Ask. The analysis continues when you answer.
        </p>
      ) : isStale ? (
        <p className="text-sm font-semibold text-mark">
          The analysis is out of date. Sources changed since it was made. Use Analyze at the top.
        </p>
      ) : (
        <p className="text-sm text-ink-secondary">
          Not analyzed yet. Use Analyze at the top when the sources are ready.
        </p>
      )}
      {isUploading && <p className="mt-1 text-xs text-ink-secondary">Reading the new file…</p>}
    </div>
  );
}

function SourceCheckbox({
  source,
  title,
  isAnalysing,
  disabled,
  onChange,
}: {
  source: CaseSourceRead;
  title: string;
  isAnalysing: boolean;
  disabled: boolean;
  onChange: (sourceId: string, active: boolean) => Promise<void>;
}) {
  const included = !isTurnedOff(source);
  return (
    <label
      title={isAnalysing ? "Wait for the analysis to finish" : "Include in the analysis"}
      className={`flex h-11 w-8 shrink-0 items-start justify-center pt-3 ${
        disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer"
      }`}
    >
      <input
        type="checkbox"
        checked={included}
        disabled={disabled}
        onChange={() => void onChange(source.id, !included)}
        aria-label={`Include in the analysis: ${title}`}
        className="h-5 w-5 cursor-[inherit] accent-primary"
      />
    </label>
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
  const pages = item.kind === "file" ? documentPages(item.source).length : 0;
  const detail =
    item.kind === "file"
      ? [
          fileKind(item.source),
          `${pages} ${pages === 1 ? "page" : "pages"}`,
          readByOcr(item.source) ? "read by OCR" : formatBytes(item.source.size_bytes ?? 0),
        ].join(" · ")
      : item.kind === "followup_answer"
        ? firstLine(item.followup.answer)
        : `Typed · ${formatDate(item.source.created_at, "day")}`;
  const leftOut = item.kind !== "followup_answer" && isTurnedOff(item.source);

  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
      className={`flex min-w-0 flex-1 items-start gap-2.5 rounded-lg px-2 py-2.5 text-left transition-colors ${
        selected
          ? "text-ink"
          : leftOut
            ? "text-ink-muted hover:bg-surface-hover hover:text-ink"
            : "text-ink hover:bg-surface-hover"
      }`}
    >
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-semibold">{itemTitle(item)}</span>
        <span className="mt-0.5 block truncate text-xs text-ink-muted">
          {leftOut ? `Not used · ${detail}` : detail}
        </span>
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
        <span className="block truncate text-sm font-medium text-ink">
          {filename || "Uploading file…"}
        </span>
        <span className="mt-0.5 block text-xs text-ink-muted">Reading the file…</span>
      </span>
    </div>
  );
}
