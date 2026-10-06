import type { CaseAnalysisTrace } from "@/lib/api/types";
import { validationSummary } from "./validationSummary";

export function AnalysisPipeline({ trace }: { trace: CaseAnalysisTrace }) {
  const review = validationSummary(trace);
  return (
    <details className="mt-6 rounded-xl border border-line bg-surface">
      <summary className="cursor-pointer px-4 py-3 text-[13px] font-medium text-ink">
        Analysis pipeline{" "}
        <span className="ml-2 font-normal text-ink-secondary">
          {trace.claims.length} claims
          {review.sourceUnits &&
            ` · ${review.sourceUnits.resolved}/${review.sourceUnits.claimed} source unit IDs resolved`}
        </span>
      </summary>
      <div className="space-y-5 border-t border-line px-4 py-4 text-[13px] leading-6">
        <p className="text-ink-secondary">Reading → Source binding → Claim views → Judgement</p>
        <div className="grid gap-6 sm:grid-cols-2">
          <section aria-label="Source binding">
            <h2 className="font-semibold text-ink">Source binding</h2>
            {review.sourceUnits ? (
              <>
                <dl className="mt-2 space-y-1">
                  <Count label="Source unit IDs selected" value={review.sourceUnits.claimed} />
                  <Count label="Resolved IDs" value={review.sourceUnits.resolved} />
                  <Count label="Invalid IDs" value={review.sourceUnits.invalid} />
                  <Count
                    label="ID resolution rate"
                    value={
                      review.sourceUnits.rate === null
                        ? "Not recorded"
                        : `${(review.sourceUnits.rate * 100).toFixed(1)}%`
                    }
                  />
                </dl>
                <p className="mt-2 text-xs text-ink-muted">
                  Resolved IDs locate original source text. They do not establish semantic support.
                </p>
              </>
            ) : (
              <p className="mt-2 text-ink-secondary">No source unit ID metrics were recorded.</p>
            )}
            <dl className="mt-3 space-y-1">
              <Count label="Claims with direct source citations" value={review.claims.direct} />
              <Count
                label="Claims with recovered source citations"
                value={review.claims.recovered}
              />
              <Count
                label="Claims without resolved source citations"
                value={review.claims.unresolved}
              />
              {review.claims.legacy > 0 && (
                <Count label="Claims with legacy source citations" value={review.claims.legacy} />
              )}
            </dl>
            <p className="mt-2 text-xs text-ink-muted">
              Claim counts may overlap when a claim uses more than one citation method.
            </p>
          </section>
          {review.total > 0 && (
            <section aria-label="Saved description checks">
              <h2 className="font-semibold text-ink">Saved description checks</h2>
              <p className="mt-1 text-ink-secondary">
                This earlier analysis contains separate party, timeline or impact descriptions. New
                analyses record those facts in claims.
              </p>
              <dl className="mt-2 space-y-1">
                <Count label="Descriptions" value={review.total} />
                <Count label="Supported by linked claims" value={review.counts.supported} />
                <Count label="Not supported by linked claims" value={review.counts.not_supported} />
                <Count label="Not assessed" value={review.counts.unassessed} />
                {review.counts.not_recorded > 0 && (
                  <Count label="Check not recorded" value={review.counts.not_recorded} />
                )}
              </dl>
              {review.reasons.length > 0 && (
                <ul
                  className="mt-3 space-y-1 text-ink-secondary"
                  aria-label="Why descriptions were not assessed"
                >
                  {review.reasons.map((item) => (
                    <li key={item.reason}>
                      {item.count} · {item.description}
                    </li>
                  ))}
                </ul>
              )}
              <p className="mt-3 text-ink-secondary">
                Recorded earlier Judgement use: {review.admitted} descriptions admitted;{" "}
                {review.withheld} withheld.
              </p>
              {review.counts.not_recorded > 0 && (
                <p className="mt-1 text-xs text-ink-muted">
                  Judgement use was not recorded for {review.counts.not_recorded} descriptions in
                  this saved analysis.
                </p>
              )}
            </section>
          )}
          {trace.view_extraction && (
            <section aria-label="Claim views">
              <h2 className="font-semibold text-ink">Claim views</h2>
              <p className="mt-1 text-ink-secondary">
                GLiNER2 organizes information from grounded claims for Details and reports.
              </p>
              <dl className="mt-2 space-y-1">
                <Count
                  label="Claims processed"
                  value={trace.view_extraction.input_claim_ids.length}
                />
                <Count
                  label="Claims without resolved support omitted"
                  value={trace.view_extraction.excluded_claim_ids.length}
                />
                <Count label="Parties" value={trace.involved_parties?.length ?? 0} />
                <Count label="Timeline entries" value={trace.timeline?.length ?? 0} />
                <Count label="Impacts" value={trace.impacts?.length ?? 0} />
                <Count
                  label="Extraction time"
                  value={`${(trace.view_extraction.duration_ms / 1000).toFixed(2)}s`}
                />
              </dl>
              <p className="mt-2 text-xs text-ink-muted">
                Field locations are checked against claim text. Name-role and time-event
                relationships have no semantic verdict. These views are not supplied to Judgement.
              </p>
            </section>
          )}
        </div>
        <section aria-label="Judgement input" className="border-t border-line pt-3">
          <h2 className="font-semibold text-ink">Judgement input</h2>
          <p className="mt-1 text-ink-secondary">
            New analyses supply canonical claims and their resolved source content to Judgement.
            People, dates, events and impacts remain in those claims. Extracted views are used for
            display.
          </p>
          <p className="mt-1 text-xs text-ink-muted">
            Source binding validates references and reproduces original text. It does not verify
            that the text supports every claim or guarantee the final summary.
          </p>
        </section>
      </div>
    </details>
  );
}

function Count({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-baseline justify-between gap-4">
      <dt className="text-ink-secondary">{label}</dt>
      <dd className="shrink-0 font-medium tabular-nums text-ink">{value}</dd>
    </div>
  );
}
