import Link from "next/link";
import { Icon } from "@/components/common/icons";
import type { CaseRead } from "@/lib/api";
import {
  analysisFreshnessLabel,
  caseDestination,
  caseStatusLabel,
  caseStatusTone,
  formatCaseDate,
  toneDotClass,
  type CaseLibraryViewMode,
} from "./caseDisplay";

/** Where a case stands, as a coloured dot and a phrase. */
export function CaseStatus({ caseRecord }: { caseRecord: CaseRead }) {
  return (
    <span className="inline-flex items-center gap-2">
      <span
        className={`h-1.5 w-1.5 rounded-full ${toneDotClass[caseStatusTone(caseRecord)]}`}
        aria-hidden="true"
      />
      {caseStatusLabel(caseRecord)}
    </span>
  );
}

function OpenCase({ large = false }: { large?: boolean }) {
  return (
    <span
      className={
        large
          ? "inline-flex shrink-0 items-center gap-2 text-xs font-bold text-accent transition-transform group-hover:translate-x-0.5"
          : "inline-flex shrink-0 items-center gap-1 text-[11px] font-semibold text-ink-secondary transition-colors group-hover:text-accent"
      }
    >
      Open case
      <Icon name="external" className={large ? "h-3.5 w-3.5" : "h-3 w-3"} />
    </span>
  );
}

/** The case worked on most recently, given room at the top of the library. */
export function FeaturedCaseCard({ caseRecord }: { caseRecord: CaseRead }) {
  return (
    <Link
      href={caseDestination(caseRecord)}
      className="group block rounded-md border border-line bg-surface p-4 outline-none transition-colors hover:border-line-strong hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-accent sm:p-5"
    >
      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] font-semibold text-ink-muted">
            <CaseStatus caseRecord={caseRecord} />
            <span>Updated {formatCaseDate(caseRecord.updated_at)}</span>
          </div>

          <h3
            className="mt-2 truncate text-xl font-semibold tracking-[-0.025em] text-ink sm:text-2xl"
            title={caseRecord.title}
          >
            {caseRecord.title}
          </h3>

          <p className="mt-2 text-xs text-ink-muted">
            Source revision {caseRecord.source_revision}
          </p>
        </div>

        <OpenCase large />
      </div>
    </Link>
  );
}

interface CaseCardProps {
  caseRecord: CaseRead;
  viewMode: CaseLibraryViewMode;
  isDeleting?: boolean;
  onRequestDelete?: (caseRecord: CaseRead) => void;
}

export function CaseCard({ caseRecord, viewMode, isDeleting, onRequestDelete }: CaseCardProps) {
  const isList = viewMode === "list";

  return (
    <article className="group relative rounded-md border border-line bg-surface transition-colors hover:border-line-strong hover:bg-surface-hover">
      {onRequestDelete && (
        <button
          type="button"
          aria-label={`Delete ${caseRecord.title}`}
          title={`Delete ${caseRecord.title}`}
          disabled={isDeleting}
          onClick={() => onRequestDelete(caseRecord)}
          className="absolute right-2 top-2 z-10 flex h-7 w-7 items-center justify-center rounded-md text-ink-muted opacity-0 outline-none transition-opacity hover:bg-surface-hover hover:text-critical focus-visible:opacity-100 focus-visible:ring-2 focus-visible:ring-accent group-hover:opacity-100 disabled:cursor-wait disabled:opacity-40"
        >
          <Icon name="trash" className="h-3.5 w-3.5" />
        </button>
      )}

      <Link
        href={caseDestination(caseRecord)}
        className={`block outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent ${
          isList ? "px-4 py-3.5 sm:px-5" : "min-h-48 p-4 sm:p-5"
        }`}
      >
        <div className="flex items-start justify-between gap-3 text-[10px] font-semibold text-ink-muted">
          <CaseStatus caseRecord={caseRecord} />
          <span className="shrink-0 pr-7 font-normal">{formatCaseDate(caseRecord.updated_at)}</span>
        </div>

        <div
          className={
            isList
              ? "mt-1 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between"
              : "mt-8"
          }
        >
          <h3
            className="max-w-xl truncate text-base font-semibold tracking-[-0.015em] text-ink sm:text-lg"
            title={caseRecord.title}
          >
            {caseRecord.title}
          </h3>
          <OpenCase />
        </div>

        <div
          className={`flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-ink-muted ${
            isList ? "mt-2" : "mt-6 border-t border-line/70 pt-3"
          }`}
        >
          <span>Source revision {caseRecord.source_revision}</span>
          <span aria-hidden="true">·</span>
          <span>{analysisFreshnessLabel(caseRecord)}</span>
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
        <span className="max-w-48 text-[11px] leading-5 text-ink-muted">
          Start a new source-bound investigation.
        </span>
      </button>
    </article>
  );
}
