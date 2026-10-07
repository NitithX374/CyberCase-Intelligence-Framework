import type { CaseAnalysisTrace } from "@/lib/api/types";

export function AnalysisPipeline({ trace }: { trace: CaseAnalysisTrace }) {
  const linked = trace.claims.filter((claim) => (claim.supporting_citations?.length ?? 0) > 0).length;
  const needsReview = trace.claims.length - linked;

  return (
    <details className="mt-6 rounded-xl border border-line bg-surface">
      <summary className="cursor-pointer px-4 py-3 text-[13px] font-medium text-ink">
        How this analysis was prepared
      </summary>
      <div className="space-y-4 border-t border-line px-4 py-4 text-[13px] leading-6">
        <p className="text-ink-secondary">Sources → Findings → Summary and case details</p>
        <dl className="space-y-1">
          <Count label="Findings" value={trace.claims.length} />
          <Count label="Findings with linked sources" value={linked} />
          {needsReview > 0 && <Count label="Findings needing source review" value={needsReview} />}
          <Count label="People and organizations" value={trace.involved_parties?.length ?? 0} />
          <Count label="Timeline events" value={trace.timeline?.length ?? 0} />
          <Count label="Impacts" value={trace.impacts?.length ?? 0} />
        </dl>
        {trace.view_extraction?.status === "failed" && (
          <p className="text-ink-secondary">
            People, timeline and impacts could not be prepared. The summary is available.
          </p>
        )}
        {(trace.view_extraction?.items_dropped ?? 0) > 0 && (
          <p className="text-ink-secondary">
            Some case details were omitted because they could not be linked to this analysis.
          </p>
        )}
        <p className="text-xs text-ink-muted">
          Findings link back to the original sources. Case details organize those findings. Open a
          source link to review the original text; a link alone does not establish that a statement
          is correct.
        </p>
      </div>
    </details>
  );
}

function Count({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-baseline justify-between gap-4">
      <dt className="text-ink-secondary">{label}</dt>
      <dd className="shrink-0 font-medium tabular-nums text-ink">{value}</dd>
    </div>
  );
}
