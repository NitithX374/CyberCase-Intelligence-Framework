import Link from "next/link";
import { Icon } from "@/components/common/icons";
import type { CaseRead } from "@/lib/api";
import {
  caseDestination,
  caseStatusLabel,
  caseStatusTone,
  formatCaseDate,
} from "./caseLibraryFormatters";
import type { CaseLibraryViewMode } from "./CaseLibraryToolbar";

interface CaseLibraryCardProps {
  caseRecord: CaseRead;
  viewMode: CaseLibraryViewMode;
}
export function CaseLibraryCard({ caseRecord, viewMode }: CaseLibraryCardProps) {
  const tone = caseStatusTone(caseRecord);
  const toneClass = {
    neutral: "bg-ink-muted",
    positive: "bg-established",
    attention: "bg-unresolved",
    critical: "bg-critical",
  }[tone];

  return (
    <article className={`group border border-line bg-surface transition-colors hover:border-line-strong hover:bg-surface-hover ${viewMode === "list" ? "rounded-md" : "rounded-md"}`}>
      <Link
        href={caseDestination(caseRecord)}
        className={`block outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent ${viewMode === "list" ? "px-4 py-3.5 sm:px-5" : "min-h-48 p-4 sm:p-5"}`}
      >
        <div className="flex items-start justify-between gap-3">
          <span className="inline-flex items-center gap-2 text-[10px] font-semibold text-ink-muted">
            <span className={`h-1.5 w-1.5 rounded-full ${toneClass}`} aria-hidden="true" />
            {caseStatusLabel(caseRecord)}
          </span>
          <span className="shrink-0 text-[10px] text-ink-muted">
            {formatCaseDate(caseRecord.updated_at)}
          </span>
        </div>

        <div className={viewMode === "list" ? "mt-1 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between" : "mt-8"}>
          <h3 className="max-w-xl truncate text-base font-semibold tracking-[-0.015em] text-ink sm:text-lg" title={caseRecord.title}>
            {caseRecord.title}
          </h3>
          <span className="inline-flex shrink-0 items-center gap-1 text-[11px] font-semibold text-ink-secondary transition-colors group-hover:text-accent">
            Open case
            <Icon name="external" className="h-3 w-3" />
          </span>
        </div>

        <div className={`flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-ink-muted ${viewMode === "list" ? "mt-2" : "mt-6 border-t border-line/70 pt-3"}`}>
          <span>Evidence revision {caseRecord.evidence_revision}</span>
          <span aria-hidden="true">·</span>
          <span>{caseRecord.analysis_freshness === "current" ? "Current analysis" : caseRecord.analysis_freshness === "stale" ? "Older analysis" : "Analysis unavailable"}</span>
        </div>
      </Link>
    </article>
  );
}

export function NewCaseCard({ onClick, disabled }: { onClick: () => void; disabled: boolean }) {
  return (
    <article className="rounded-md border border-dashed border-line-strong bg-surface">
      <button
        type="button"
        onClick={onClick}
        disabled={disabled}
        className="flex min-h-48 w-full flex-col items-center justify-center gap-3 p-5 text-center text-ink outline-none transition-colors hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent disabled:cursor-wait disabled:opacity-60"
      >
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-soft text-accent">
          <Icon name="plus" className="h-5 w-5" />
        </span>
        <span className="text-sm font-semibold">Create a new case</span>
        <span className="max-w-48 text-[11px] leading-5 text-ink-muted">Start a new evidence-bound investigation.</span>
      </button>
    </article>
  );
}
