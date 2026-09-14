"use client";

import { useMemo } from "react";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead } from "@/lib/api";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { buildCaseOverview } from "@/lib/case-overview-builder";

interface CaseAnalysisLeadCardProps {
  result: CaseAnalysisResultRead;
  snapshot?: CaseEvidenceSnapshotRead | null;
  isUpdated?: boolean;
  onOpenOverview?: () => void;
}

export function CaseAnalysisLeadCard({
  result,
  snapshot,
  isUpdated = false,
  onOpenOverview,
}: CaseAnalysisLeadCardProps) {
  const summaryText = result.summary?.trim() || result.answer?.trim() || "";
  const isValidated = result.status === "validated";
  const overview = useMemo(() => buildCaseOverview(result, snapshot ?? null, null), [result, snapshot]);
  const findingCount = overview.hasAnalysis ? overview.findings.length : 0;
  const openQuestionCount = overview.hasAnalysis ? overview.gaps.length : 0;
  const freshnessLabel = result.freshness === "stale"
    ? "Based on older evidence"
    : result.freshness === "current"
      ? "Current"
      : "Freshness unavailable";

  return (
    <aside
      aria-label="Analysis Result"
      className="mb-5 overflow-hidden rounded-md border border-line bg-surface p-4 sm:p-5"
    >
      <header className="flex flex-wrap items-start justify-between gap-3 border-b border-line pb-3">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-ink">Analysis Result</span>
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
            aria-label="View full Case Overview"
            className="text-[11px] font-semibold text-evidence transition-colors hover:text-accent-strong hover:underline"
          >
            Open full analysis
          </button>
        )}
      </header>

      <div className="mt-4 space-y-4">
        <div>
          <h3 className="text-sm font-bold text-ink">{isUpdated ? "Updated analysis" : "Analysis complete"}</h3>
        </div>
        <div className="text-sm leading-relaxed text-ink">
          <ChatMessageMarkdown content={summaryText} />
        </div>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 border-t border-line pt-3 sm:grid-cols-4">
          <Metric label="Findings" value={String(findingCount)} />
          <Metric label="Open questions" value={String(openQuestionCount)} />
          <Metric
            label={Array.isArray(snapshot) ? "Sources" : "Evidence revision"}
            value={
              !snapshot
                ? "—"
                : Array.isArray(snapshot)
                  ? String(snapshot.length)
                  : "evidence_revision" in snapshot && snapshot.evidence_revision !== undefined
                    ? String(snapshot.evidence_revision)
                    : "—"
            }
          />
          <Metric label="Analysis state" value={freshnessLabel} emphasis={result.freshness === "stale" ? "attention" : "positive"} />
        </dl>
        <p className="text-[10px] leading-relaxed text-ink-muted">Ask uses this persisted result. Ordinary questions do not change evidence.</p>
      </div>
    </aside>
  );
}

function Metric({
  label,
  value,
  emphasis,
}: {
  label: string;
  value: string;
  emphasis?: "positive" | "attention";
}) {
  return (
    <div className="min-w-0">
      <dt className="text-[10px] font-medium text-ink-muted">{label}</dt>
      <dd className={`mt-1 truncate text-xs font-bold ${emphasis === "attention" ? "text-unresolved" : emphasis === "positive" ? "text-established" : "text-ink"}`}>
        {value}
      </dd>
    </div>
  );
}
