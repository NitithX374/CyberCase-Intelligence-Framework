import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import { hasThai } from "@/lib/language";
import { PROJECTION_LABELS, projectionReason, projectionStatus } from "./projectionChecks";
import type { ClaimBacked } from "./types";
import { ClaimViewReview } from "./ClaimViewReview";

export function ProjectionReview({ row, caseId }: { row: ClaimBacked; caseId?: string }) {
  if (row.fieldSpans && Object.keys(row.fieldSpans).length > 0) {
    return <ClaimViewReview row={row} caseId={caseId} />;
  }
  const grounding = row.projectionGrounding;
  const status = projectionStatus(grounding);
  const claims = row.linkedClaims ?? [];
  return (
    <details className="mt-2 text-xs leading-6 text-ink-secondary">
      <summary className="cursor-pointer font-medium">
        {PROJECTION_LABELS[status]} ·{" "}
        {status === "supported"
          ? "Used in earlier Judgement"
          : status === "not_recorded"
            ? "Judgement use not recorded"
            : "Withheld from earlier Judgement"}
      </summary>
      <div className="mt-2 space-y-2 border-l border-line pl-3">
        {grounding ? (
          <p>
            {projectionReason(
              grounding,
              claims.some((claim) => hasThai(claim.text)),
            )}
          </p>
        ) : (
          <p>
            This saved description has no recorded semantic check or Judgement admission status.
          </p>
        )}
        {grounding?.model && (
          <p className="break-all text-ink-muted">Verifier: {grounding.model}</p>
        )}
        <p>
          {status === "supported"
            ? "The saved description was included in the earlier Judgement's case descriptions."
            : status === "not_recorded"
              ? "The saved record does not show whether this description was supplied to Judgement."
              : "The saved description was excluded from the earlier Judgement's case descriptions. Its linked claims were still supplied."}
        </p>
        {claims.length > 0 ? (
          <ul className="space-y-2" aria-label="Linked claims">
            {claims.map((claim) => (
              <li key={claim.id}>
                {caseId ? (
                  <Link
                    href={`${analysisPath(caseId, "findings")}?finding=${encodeURIComponent(claim.id)}`}
                    className="font-medium underline underline-offset-2"
                  >
                    {claim.id}
                  </Link>
                ) : (
                  <span className="font-medium">{claim.id}</span>
                )}{" "}
                — {claim.text}
              </li>
            ))}
          </ul>
        ) : (
          <p>No linked claims were recorded.</p>
        )}
        <p className="text-ink-muted">Source citations above belong to the linked claims.</p>
      </div>
    </details>
  );
}
