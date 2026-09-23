import Link from "next/link";
import { Icon } from "@/components/common/icons";
import type { CaseRead } from "@/lib/api";
import { formatDate } from "@/lib/format";
import {
  caseDestination,
  caseStatusLabel,
  caseStatusTone,
  toneDotClass,
  type CaseLibraryViewMode,
} from "./caseDisplay";

/** Where a case stands, as a coloured dot and a word or two. */
export function CaseStatus({ caseRecord }: { caseRecord: CaseRead }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span
        className={`h-1.5 w-1.5 rounded-full ${toneDotClass[caseStatusTone(caseRecord)]}`}
        aria-hidden="true"
      />
      {caseStatusLabel(caseRecord)}
    </span>
  );
}

interface CaseCardProps {
  caseRecord: CaseRead;
  viewMode: CaseLibraryViewMode;
  isDeleting?: boolean;
  onRequestDelete?: (caseRecord: CaseRead) => void;
}

export function CaseCard({ caseRecord, viewMode, isDeleting, onRequestDelete }: CaseCardProps) {
  const deleteButton = onRequestDelete && (
    <button
      type="button"
      aria-label={`Delete ${caseRecord.title}`}
      title="Delete case"
      disabled={isDeleting}
      onClick={() => onRequestDelete(caseRecord)}
      className="icon-btn relative z-10 opacity-0 group-hover:opacity-100 hover:text-critical focus-visible:opacity-100 disabled:cursor-wait max-md:opacity-100"
    >
      <Icon name="trash" className="h-4 w-4" />
    </button>
  );

  if (viewMode === "list") {
    return (
      <li className="group relative flex items-center gap-3 rounded-lg px-3 transition-colors hover:bg-surface-hover">
        <Link
          href={caseDestination(caseRecord)}
          className="flex min-w-0 flex-1 items-center gap-4 py-3.5 after:absolute after:inset-0 after:content-['']"
        >
          <span className="min-w-0 flex-1">
            <span
              className="block truncate text-[15px] font-semibold tracking-[-0.01em] text-ink"
              title={caseRecord.title}
            >
              {caseRecord.title}
            </span>
            <span className="mt-0.5 block text-[13px] text-ink-muted">
              <CaseStatus caseRecord={caseRecord} />
            </span>
          </span>
          <span className="hidden shrink-0 text-[13px] text-ink-muted sm:block">
            {formatDate(caseRecord.updated_at)}
          </span>
        </Link>
        {deleteButton}
      </li>
    );
  }

  return (
    <li className="group relative flex min-h-36 flex-col justify-between rounded-xl border border-line bg-surface p-5 transition-colors hover:border-line-strong">
      <div className="flex items-start justify-between gap-3 text-[13px] text-ink-muted">
        <CaseStatus caseRecord={caseRecord} />
        <span className="-mt-1.5 -mr-2">{deleteButton}</span>
      </div>
      <Link
        href={caseDestination(caseRecord)}
        className="mt-6 block after:absolute after:inset-0 after:rounded-xl after:content-['']"
      >
        <span
          className="line-clamp-2 text-base font-semibold tracking-[-0.01em] text-ink"
          title={caseRecord.title}
        >
          {caseRecord.title}
        </span>
        <span className="mt-1 block text-[13px] text-ink-muted">
          {formatDate(caseRecord.updated_at)}
        </span>
      </Link>
    </li>
  );
}
