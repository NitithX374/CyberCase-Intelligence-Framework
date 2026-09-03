import { useState } from "react";
import { Icon } from "@/components/common/icons";
import type { ThreadStatus } from "@/lib/api";

const statusLabels: Record<ThreadStatus, string> = {
  idle: "Idle", processing: "Analyzing", awaiting_followup: "Awaiting clarification",
  answered: "Analysis available", failed: "Run failed",
};

interface CaseOverviewHeaderProps {
  threadId: string;
  threadTitle: string;
  threadStatus: ThreadStatus;
  onOpenChat: () => void;
  onOpenReport: () => void;
  onOpenMaterials?: () => void;
}

export function CaseOverviewHeader({
  threadId, threadTitle, threadStatus, onOpenChat, onOpenReport, onOpenMaterials,
}: CaseOverviewHeaderProps) {
  const [showFullTitle, setShowFullTitle] = useState(false);
  return (
    <header className="space-y-4 border-b border-line pb-5">
      <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-ink-muted">
        <span className="min-w-0 break-all font-mono">Case {threadId}</span>
        <span>{statusLabels[threadStatus]}</span>
      </div>
      <h1 className={`max-w-4xl text-xl font-semibold leading-snug tracking-tight text-ink [overflow-wrap:anywhere] sm:text-2xl ${threadTitle.length > 120 && !showFullTitle ? "line-clamp-2" : ""}`}>
        {threadTitle}
      </h1>
      {threadTitle.length > 120 && (
        <button type="button" aria-expanded={showFullTitle} onClick={() => setShowFullTitle(!showFullTitle)}
          className="text-xs text-ink-secondary underline underline-offset-4 focus-visible:ring-2 focus-visible:ring-primary">
          {showFullTitle ? "Shorten title" : "Read full title"}
        </button>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" onClick={onOpenChat} className="btn-secondary inline-flex items-center gap-1.5 rounded-lg">
          <Icon name="chat" className="h-3.5 w-3.5" />Ask about this case
        </button>
        <button type="button" onClick={onOpenReport} className="btn-primary inline-flex items-center gap-1.5 rounded-lg">
          <Icon name="report" className="h-3.5 w-3.5" />View Report
        </button>
        {onOpenMaterials && (
          <button type="button" onClick={onOpenMaterials}
            className="min-h-9 px-2 text-xs text-ink-secondary underline decoration-line-strong underline-offset-4 hover:text-ink focus-visible:ring-2 focus-visible:ring-primary">
            All sources
          </button>
        )}
      </div>
    </header>
  );
}
