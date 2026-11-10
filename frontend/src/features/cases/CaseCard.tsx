import Link from "next/link";
import { Icon } from "@/components/icons";
import type { CaseRead } from "@/lib/api/types";
import { formatDate } from "@/lib/format";
import { caseDestination, caseStatusLabel, type CaseLibraryViewMode } from "./caseDisplay";

function CaseStatus({ caseRecord }: { caseRecord: CaseRead }) {
  const freshness = caseRecord.analysis_freshness;
  return (
    <span
      className={
        freshness === "stale"
          ? "badge-check"
          : freshness === "current"
            ? "badge-linked"
            : "count-pill px-2.5"
      }
    >
      {caseStatusLabel(caseRecord)}
    </span>
  );
}

interface CaseCardProps {
  caseRecord: CaseRead;
  viewMode: CaseLibraryViewMode;
  isDeleting?: boolean;
  onRequestDelete?: (caseRecord: CaseRead) => void;
  index?: number;
}

export function CaseCard({
  caseRecord,
  viewMode,
  isDeleting,
  onRequestDelete,
  index = 0,
}: CaseCardProps) {
  const stagger = { ["--i" as string]: Math.min(index, 8) };
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
      <li
        style={stagger}
        className="group stagger row-accent relative flex items-center gap-3 px-5 transition-colors hover:bg-primary-wash sm:px-6"
      >
        <Link
          href={caseDestination(caseRecord)}
          className="flex min-w-0 flex-1 items-center gap-4 py-4 after:absolute after:inset-0 after:content-['']"
        >
          <span
            className="min-w-0 flex-1 truncate text-base font-semibold text-ink"
            title={caseRecord.title}
          >
            {caseRecord.title}
          </span>
          <span className="shrink-0 text-sm">
            <CaseStatus caseRecord={caseRecord} />
          </span>
          <span className="hidden w-32 shrink-0 text-right text-sm text-ink-muted sm:block">
            {formatDate(caseRecord.updated_at)}
          </span>
        </Link>
        {deleteButton}
      </li>
    );
  }

  return (
    <li
      style={stagger}
      className="group stagger lift relative flex min-h-36 flex-col justify-between rounded-[10px] border border-line bg-surface p-5 hover:border-primary-line hover:bg-primary-wash"
    >
      <div className="flex items-start justify-between gap-3 text-sm text-ink-muted">
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
        <span className="mt-1 block text-sm text-ink-muted">
          {formatDate(caseRecord.updated_at)}
        </span>
      </Link>
    </li>
  );
}
