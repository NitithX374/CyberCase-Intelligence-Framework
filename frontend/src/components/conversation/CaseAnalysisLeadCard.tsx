"use client";

import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead } from "@/lib/api";
import { Icon } from "@/components/common/icons";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";

interface CaseAnalysisLeadCardProps {
  result: CaseAnalysisResultRead;
  snapshot?: CaseEvidenceSnapshotRead | null;
  onOpenOverview?: () => void;
}

export function CaseAnalysisLeadCard({
  result,
  onOpenOverview,
}: CaseAnalysisLeadCardProps) {
  const summaryText = result.summary?.trim() || result.answer?.trim() || "";
  const isValidated = result.status === "validated";

  return (
    <aside
      aria-label="Case Analysis Lead Summary"
      className="mb-6 overflow-hidden rounded-2xl border border-line-strong/60 bg-surface-nested p-4 shadow-sm sm:p-5"
    >
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-line pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-5 w-5 items-center justify-center rounded-md bg-accent text-ivory">
            <Icon name="overview" className="h-3 w-3" />
          </div>
          <span className="text-[11px] font-bold uppercase tracking-[0.08em] text-ink">
            Grounded Case Analysis
          </span>
          {isValidated && (
            <span className="inline-flex items-center gap-1 rounded-full bg-established/10 px-2 py-0.5 text-[10px] font-semibold text-established">
              <span className="h-1.5 w-1.5 rounded-full bg-established" />
              Validated
            </span>
          )}
        </div>
        {onOpenOverview && (
          <button
            type="button"
            onClick={onOpenOverview}
            className="text-[11px] font-medium text-ink-muted transition-colors hover:text-ink hover:underline"
          >
            View full Case Overview →
          </button>
        )}
      </header>

      <div className="mt-3.5 space-y-3">
        <div className="text-sm leading-relaxed text-ink">
          <ChatMessageMarkdown content={summaryText} />
        </div>
        <p className="text-[10px] text-ink-muted">
          Anchor for Case Q&A. Questions in this chat are evaluated against this validated analysis.
        </p>
      </div>
    </aside>
  );
}
