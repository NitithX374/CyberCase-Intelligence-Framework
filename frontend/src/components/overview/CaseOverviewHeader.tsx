import { Icon } from "@/components/common/icons";
import { ThreadStatusPill } from "@/components/common/ThreadStatusPill";
import type { ThreadStatus } from "@/lib/api";

interface CaseOverviewHeaderProps {
  threadTitle: string;
  threadStatus: ThreadStatus;
  onOpenChat: () => void;
  onOpenReport: () => void;
  onOpenMaterials?: () => void;
}

export function CaseOverviewHeader({
  threadTitle,
  threadStatus,
  onOpenChat,
  onOpenReport,
  onOpenMaterials,
}: CaseOverviewHeaderProps) {
  return (
    <header className="border-b border-line pb-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="section-eyebrow">CASE FILE / OVERVIEW</p>
          <h1 className="mt-1 max-w-3xl text-2xl font-extrabold tracking-[-0.035em] text-ink sm:text-3xl">
            {threadTitle}
          </h1>
          <p className="mt-2 text-xs leading-relaxed text-ink-secondary">
            Evidence-bound case review with source traceability and clearly separated analytical context.
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          <ThreadStatusPill status={threadStatus} />
        </div>
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={onOpenChat}
          className="btn-secondary inline-flex items-center gap-1.5 rounded-lg"
        >
          <Icon name="chat" className="h-3.5 w-3.5" />
          Ask about this case
        </button>
        {onOpenMaterials && (
          <button
            type="button"
            onClick={onOpenMaterials}
            className="btn-secondary inline-flex items-center gap-1.5 rounded-lg"
          >
            <Icon name="materials" className="h-3.5 w-3.5" />
            View sources
          </button>
        )}
        <button
          type="button"
          onClick={onOpenReport}
          className="btn-primary inline-flex items-center gap-1.5 rounded-lg"
        >
          <Icon name="report" className="h-3.5 w-3.5" />
          View Report
        </button>
      </div>
    </header>
  );
}
