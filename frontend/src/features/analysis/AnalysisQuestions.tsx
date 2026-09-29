"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import type { CaseGap } from "@/features/analysis/types";
import { DisclosurePanel, DisclosureToggle } from "@/components/Disclosure";
import { useCaseOverview } from "./useCaseOverview";

const gapLabels: Record<CaseGap["status"], string> = {
  NOT_PROVIDED: "Missing",
  EXPLICITLY_UNKNOWN: "Unknown",
  AMBIGUOUS: "Ambiguous",
  CONFLICTING: "Conflicting",
};

const gapTextClass: Record<CaseGap["status"], string> = {
  CONFLICTING: "text-critical",
  AMBIGUOUS: "text-unresolved",
  NOT_PROVIDED: "text-unresolved",
  EXPLICITLY_UNKNOWN: "text-ink-secondary",
};

export function AnalysisQuestions() {
  const { caseId } = useParams<{ caseId: string }>();
  const { overview } = useCaseOverview(caseId);
  if (!overview.hasAnalysis) return null;

  return (
    <div className="mx-auto w-full max-w-[52rem] px-5 sm:px-8">
      {overview.gaps.length === 0 ? (
        <p className="py-6 text-sm text-ink-muted">Nothing is missing from this analysis.</p>
      ) : (
        <ul aria-label="Open questions" className="divide-y divide-line pt-2">
          {overview.gaps.map((gap) => (
            <OpenQuestionRow key={gap.id} gap={gap} />
          ))}
        </ul>
      )}
    </div>
  );
}

function OpenQuestionRow({ gap }: { gap: CaseGap }) {
  const [isOpen, setIsOpen] = useState(false);
  const reasonId = `gap-${gap.id}-reason`;
  return (
    <li className="grid gap-x-4 gap-y-1.5 py-4 sm:grid-cols-[6.5rem_minmax(0,1fr)]">
      <div className="flex flex-wrap items-start gap-1.5 sm:pt-0.5">
        <span className={`text-[13px] font-medium ${gapTextClass[gap.status]}`}>
          {gapLabels[gap.status]}
        </span>
      </div>
      <div className="min-w-0">
        <h3 className="text-[15px] font-semibold leading-6 text-ink">{gap.topic}</h3>
        <p className="mt-0.5 text-sm leading-6 text-ink-secondary">{gap.description}</p>
        {(gap.askable || gap.reason) && (
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
            {gap.askable && (
              <span className="text-xs font-medium text-ink-secondary">Needs an answer</span>
            )}
            {gap.reason && (
              <DisclosureToggle
                label="Why it matters"
                isOpen={isOpen}
                onToggle={() => setIsOpen((open) => !open)}
                controls={reasonId}
              />
            )}
          </div>
        )}
        {gap.reason && isOpen && (
          <DisclosurePanel id={reasonId} className="mt-2">
            {gap.reason}
          </DisclosurePanel>
        )}
      </div>
    </li>
  );
}
