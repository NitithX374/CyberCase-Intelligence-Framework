"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import type { CaseGap } from "@/features/analysis/types";
import { DisclosurePanel, DisclosureToggle } from "@/components/Disclosure";
import { Icon } from "@/components/icons";
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

export function AnalysisQuestionsCard() {
  const { caseId } = useParams<{ caseId: string }>();
  const { overview } = useCaseOverview(caseId);
  if (!overview.hasAnalysis) return null;

  return (
    <section
      id="section-attention"
      aria-labelledby="questions-heading"
      className="sheet min-w-0 scroll-mt-6"
    >
      <div className="card-head bg-primary-wash">
        <h2
          id="questions-heading"
          className="flex flex-1 items-center gap-2.5 text-lg font-semibold text-ink"
        >
          <Icon name="attention" className="text-xl text-primary" />
          Open questions
        </h2>
        {overview.gaps.length > 0 && <span className="badge-check">{overview.gaps.length}</span>}
      </div>
      <div className="px-6 pb-2">
        <AnalysisQuestions />
      </div>
    </section>
  );
}

export function AnalysisQuestions() {
  const { caseId } = useParams<{ caseId: string }>();
  const { overview } = useCaseOverview(caseId);
  if (!overview.hasAnalysis) return null;

  return (
    <>
      {overview.gaps.length === 0 ? (
        <p className="py-6 text-sm text-ink-muted">Nothing is missing from this analysis.</p>
      ) : (
        <ul aria-label="Open questions" className="divide-y divide-line">
          {overview.gaps.map((gap) => (
            <OpenQuestionRow key={gap.id} gap={gap} />
          ))}
        </ul>
      )}
    </>
  );
}

function OpenQuestionRow({ gap }: { gap: CaseGap }) {
  const [isOpen, setIsOpen] = useState(false);
  const [showsFindings, setShowsFindings] = useState(false);
  const reasonId = `gap-${gap.id}-reason`;
  const findingsId = `gap-${gap.id}-findings`;
  const affected = gap.affectedFindings;
  return (
    <li className="py-4">
      <div className="min-w-0">
        <h3 className="text-sm font-semibold leading-6 text-ink">
          {gap.topic}{" "}
          <span className={`text-xs font-semibold ${gapTextClass[gap.status]}`}>
            · {gapLabels[gap.status]}
          </span>
        </h3>
        <p className="mt-0.5 text-sm leading-6 text-ink-secondary">{gap.description}</p>
        {(gap.askable || gap.reason || affected.length > 0) && (
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
            {affected.length > 0 && (
              <DisclosureToggle
                label={`Affected findings (${affected.length})`}
                isOpen={showsFindings}
                onToggle={() => setShowsFindings((open) => !open)}
                controls={findingsId}
              />
            )}
          </div>
        )}
        {gap.reason && isOpen && (
          <DisclosurePanel id={reasonId} className="mt-2">
            {gap.reason}
          </DisclosurePanel>
        )}
        {affected.length > 0 && showsFindings && (
          <DisclosurePanel id={findingsId} className="mt-2">
            <ul aria-label="Affected findings" className="space-y-1">
              {affected.map((finding) => (
                <li key={finding.id}>{finding.text}</li>
              ))}
            </ul>
          </DisclosurePanel>
        )}
      </div>
    </li>
  );
}
