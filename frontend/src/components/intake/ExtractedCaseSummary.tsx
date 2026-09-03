import type { CaseOverviewData } from "@/lib/case-overview";
import { intakeReadableText } from "@/lib/intake-readable-text";

export function ExtractedCaseSummary({ overview, sourceCount, onReview }: {
  overview: CaseOverviewData;
  sourceCount: number;
  onReview?: () => void;
}) {
  return (
    <section aria-labelledby="extracted-case-heading" className="border-t border-line pt-5">
      <h2 id="extracted-case-heading" className="text-sm font-bold text-ink">Extracted case information</h2>
      {overview.hasAnalysis ? (
        <>
          <p className="mt-1 text-[11px] text-ink-muted">From the latest completed case analysis.</p>
          <p className="mt-3 line-clamp-3 text-xs leading-relaxed text-ink-secondary">{intakeReadableText(overview.incidentSummary)}</p>
          <dl className="mt-4 grid grid-cols-3 gap-3 text-xs">
            <div><dt className="text-ink-muted">Findings</dt><dd className="mt-1 font-semibold">{overview.findings.length}</dd></div>
            <div><dt className="text-ink-muted">Evidence messages</dt><dd className="mt-1 font-semibold">{sourceCount}</dd></div>
            <div><dt className="text-ink-muted">Open questions</dt><dd className="mt-1 font-semibold">{overview.gaps.length}</dd></div>
          </dl>
          {onReview && <button type="button" onClick={onReview} className="mt-3 min-h-9 text-xs text-ink-secondary underline underline-offset-4 hover:text-ink">Review extracted information →</button>}
        </>
      ) : <p className="mt-2 text-xs leading-relaxed text-ink-muted">Findings and open questions become available after case analysis. Document extraction prepares the text only.</p>}
    </section>
  );
}
