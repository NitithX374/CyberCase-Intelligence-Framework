import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import type { ClaimBacked } from "./types";

export function ClaimViewReview({ row, caseId }: { row: ClaimBacked; caseId?: string }) {
  return (
    <details className="mt-2 text-xs leading-6 text-ink-secondary">
      <summary className="cursor-pointer font-medium">Related findings</summary>
      <ul className="mt-2 space-y-2 border-l border-line pl-3" aria-label="Related findings">
        {(row.linkedClaims ?? []).map((claim) => (
          <li key={claim.id}>
            {caseId ? (
              <Link
                href={`${analysisPath(caseId, "findings")}?finding=${encodeURIComponent(claim.id)}`}
                className="font-medium underline underline-offset-2"
              >
                View finding
              </Link>
            ) : (
              <span className="font-medium">Finding</span>
            )}{" "}
            — {claim.text}
          </li>
        ))}
      </ul>
    </details>
  );
}
