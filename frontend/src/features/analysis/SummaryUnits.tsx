import { Fragment } from "react";
import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import type { SummaryUnit } from "./types";

export function SummaryUnits({ caseId, units }: { caseId: string; units: SummaryUnit[] }) {
  return (
    <>
      {units.map((unit, index) => (
        <p key={index}>
          {unit.text}
          {unit.claimIds.length > 0 && (
            <>
              {" ["}
              {unit.claimIds.map((claimId, position) => (
                <Fragment key={claimId}>
                  {position > 0 && ", "}
                  <Link
                    href={`${analysisPath(caseId, "findings")}?finding=${encodeURIComponent(claimId)}`}
                    className="underline underline-offset-2 hover:text-ink-secondary"
                  >
                    {claimId}
                  </Link>
                </Fragment>
              ))}
              {"]"}
            </>
          )}
          {unit.supportNote && (
            <span className="mt-0.5 block text-[13px] leading-6 text-ink-secondary">
              {unit.supportNote}
            </span>
          )}
        </p>
      ))}
    </>
  );
}
