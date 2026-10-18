"use client";

import type { CaseAnalysisClaim, ChatAnswerUnit } from "@/lib/api/types";
import type { CaseSourceRef } from "@/features/citations/types";
import { Markdown } from "@/components/Markdown";
import { stripInlineCitations } from "./inlineCitations";
import { sourceReferences, unitItem } from "./chatReferences";
import { AnswerReferences } from "./AnswerReferences";

const PRELIMINARY_NOTE = "เป็นการตีความเบื้องต้น ยังไม่ได้ผ่านการวิเคราะห์";

export function AnswerUnits({
  units,
  claims,
  sources,
}: {
  units: ChatAnswerUnit[];
  claims: CaseAnalysisClaim[];
  sources: CaseSourceRef[];
}) {
  const statuses = new Map(claims.map((claim) => [claim.claim_id, claim.epistemic_status]));
  return (
    <div className="space-y-3">
      {units.map((unit, index) => (
        <div key={index}>
          <Markdown content={stripInlineCitations(unit.text)} />
          {unit.basis === "interpretation" && (
            <p className="mt-1 text-xs text-ink-muted">{PRELIMINARY_NOTE}</p>
          )}
          <AnswerReferences {...sourceReferences([unitItem(unit, statuses)], sources)} />
        </div>
      ))}
    </div>
  );
}
