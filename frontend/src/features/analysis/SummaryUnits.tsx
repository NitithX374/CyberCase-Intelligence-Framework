import { Fragment } from "react";
import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import type { SummaryUnit } from "./types";

const WORDS = {
  thai: { finding: "ข้อ", numbers: "ตัวเลขยกคือเลขข้อค้นพบ กดเพื่อเปิดข้อนั้น" },
  english: {
    finding: "Finding",
    numbers: "Raised numbers are finding numbers; each opens its finding.",
  },
};

export function SummaryUnits({
  caseId,
  units,
  thai,
}: {
  caseId: string;
  units: SummaryUnit[];
  thai: boolean;
}) {
  const words = thai ? WORDS.thai : WORDS.english;
  const named = units.some((unit) => unit.marks.length > 0);
  return (
    <>
      <p>
        {units.map((unit, index) => (
          <Fragment key={index}>
            {index > 0 && " "}
            {unit.text}
            {unit.marks.length > 0 && (
              <sup>
                {unit.marks.map((mark, position) => (
                  <Fragment key={mark.number}>
                    {position > 0 && ","}
                    <Link
                      href={`${analysisPath(caseId, "findings")}?finding=${encodeURIComponent(mark.claimId)}`}
                      aria-label={`${words.finding} ${mark.number}`}
                      className="hover:underline focus-visible:underline"
                    >
                      {mark.number}
                    </Link>
                  </Fragment>
                ))}
              </sup>
            )}
            {unit.noteMark && <sup>{unit.noteMark}</sup>}
            {unit.closing}
          </Fragment>
        ))}
      </p>
      {named && (
        <div className="-mt-2 mb-1 text-[13px] leading-6 text-ink-secondary">{words.numbers}</div>
      )}
      {units.map((unit) =>
        unit.noteMark && unit.supportNote ? (
          <div key={unit.noteMark} className="text-[13px] leading-6 text-ink-secondary">
            <sup>{unit.noteMark}</sup> {unit.supportNote}
          </div>
        ) : null,
      )}
    </>
  );
}
