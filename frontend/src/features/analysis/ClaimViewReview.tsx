import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import type { ClaimBacked } from "./types";

export function ClaimViewReview({ row, caseId }: { row: ClaimBacked; caseId?: string }) {
  return (
    <div className="mt-2 space-y-2 border-l border-line pl-3 text-xs leading-6 text-ink-secondary">
      <p className="font-medium">Extracted from linked claims</p>
      <p>
        Use the full claim below for attribution, uncertainty and the relationship between fields.
      </p>
      <ul className="space-y-2" aria-label="Claim context">
        {(row.linkedClaims ?? []).map((claim) => (
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
      <p className="text-ink-muted">
        Extracted fields have no recorded semantic verification. Source citations belong to the
        claims.
      </p>
    </div>
  );
}
