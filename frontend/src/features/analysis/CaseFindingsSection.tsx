"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import { groupCaseFindings, claimTypeLabels } from "./overview";
import type { CaseFinding, QuotePlace } from "@/features/analysis/types";
import type { SourceMessageRef } from "@/features/citations/types";
import { SourceCitationChip } from "@/features/citations/SourceCitationChip";
import { Icon } from "@/components/icons";
import { DisclosurePanel, DisclosureToggle } from "@/components/Disclosure";

const INITIAL_FINDINGS = 5;

export interface FindingSourceActions {
  onSelectSource: (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
    citationRole?: "supporting" | "conflicting",
  ) => void;
  activeSourceKey?: string | null;
}

const groupTitleClass: Record<string, string> = {
  not_established: "text-critical",
  contradicted: "text-critical",
  not_confirmed: "text-unresolved",
  suspected: "text-unresolved",
};

export function FindingRow({
  caseId,
  finding,
  showClaimType = false,
  ...sourceActions
}: FindingSourceActions & { caseId: string; finding: CaseFinding; showClaimType?: boolean }) {
  const [isOpen, setIsOpen] = useState(false);
  const detailsId = `finding-${finding.id}-details`;

  return (
    <article id={`finding-${finding.id}`} className="scroll-mt-5 py-4">
      <p className="break-words text-[15px] leading-7 text-ink">{finding.text}</p>
      <div className="mt-2 flex flex-wrap items-center gap-1.5">
        {showClaimType && finding.claimType !== "reported" && (
          <span className="text-xs text-ink-muted">
            {finding.claimType === "analytical_inference"
              ? "Inference"
              : claimTypeLabels[finding.claimType]}
          </span>
        )}
        <SourceGroup
          sources={finding.supportingSources}
          findingId={finding.id}
          role="supporting"
          {...sourceActions}
        />
        <SourceGroup
          sources={finding.contradictingSources}
          findingId={finding.id}
          role="conflicting"
          {...sourceActions}
        />
        {finding.techniqueIds.map((techniqueId) => (
          <Link
            key={techniqueId}
            href={`${analysisPath(caseId, "details")}#mitre-${techniqueId}`}
            title={`ATT&CK ${techniqueId}`}
            className="inline-flex h-6 items-center px-1 text-xs font-medium text-ink-secondary underline-offset-2 hover:text-ink hover:underline"
          >
            {techniqueId}
          </Link>
        ))}
        {finding.reasoningSummary && (
          <DisclosureToggle
            label="Reasoning"
            isOpen={isOpen}
            onToggle={() => setIsOpen((open) => !open)}
            controls={detailsId}
            className="ml-auto"
          />
        )}
      </div>
      {finding.reasoningSummary && isOpen && (
        <DisclosurePanel id={detailsId} className="mt-3">
          {finding.reasoningSummary}
        </DisclosurePanel>
      )}
      {finding.epistemicStatus === "not_confirmed" && finding.unverifiedQuotes.length > 0 && (
        <div className="mt-2 space-y-2">
          {finding.unverifiedQuotes.map((item, index) => {
            const key = `passage-${finding.id}-${index}`;
            const passage = item.passage;
            const meaning = item.meaningPassage;
            return (
              <div key={key} className="text-sm leading-6 text-ink-secondary">
                <p>Not found word for word in the source.</p>
                {item.places.map((place, placeIndex) => (
                  <p key={placeIndex}>{placeText(place)}</p>
                ))}
                {passage && (
                  <button
                    type="button"
                    aria-haspopup="dialog"
                    onClick={(event) =>
                      sourceActions.onSelectSource(passage, event.currentTarget, key)
                    }
                    className="text-ink underline underline-offset-2 hover:text-ink-secondary"
                  >
                    Show in source
                  </button>
                )}
                {meaning && (
                  <p>
                    {meaning.quoteLabel}{" "}
                    <button
                      type="button"
                      aria-haspopup="dialog"
                      onClick={(event) =>
                        sourceActions.onSelectSource(meaning, event.currentTarget, `${key}-meaning`)
                      }
                      className="text-ink underline underline-offset-2 hover:text-ink-secondary"
                    >
                      Show in source
                    </button>
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </article>
  );
}

function placeText({ written, source }: QuotePlace): string {
  if (written && source) return `The analysis quotes «${written}»; the source says «${source}»`;
  if (written) return `The analysis adds «${written}»`;
  return `The source has «${source}», which the analysis leaves out`;
}

function SourceGroup({
  sources,
  findingId,
  role,
  onSelectSource,
  activeSourceKey,
}: FindingSourceActions & {
  sources: SourceMessageRef[];
  findingId: string;
  role: "supporting" | "conflicting";
}) {
  if (!sources.length) return null;
  return (
    <>
      {sources.map((source, index) => {
        const key = `${role}-${findingId}-${source.id}-${index}`;
        return (
          <SourceCitationChip
            key={key}
            sourceRef={source}
            sourceKey={key}
            citationRole={role}
            isActive={activeSourceKey === key}
            onSelect={onSelectSource}
          />
        );
      })}
    </>
  );
}

function groupsHolding(findings: CaseFinding[], findingId: string | null | undefined): string[] {
  if (!findingId) return [];
  return groupCaseFindings(findings)
    .filter((group) => group.findings.some((finding) => finding.id === findingId))
    .map((group) => group.id);
}

export function CaseFindingsSection({
  caseId,
  findings,
  focusId,
  ...sourceActions
}: FindingSourceActions & {
  caseId: string;
  findings: CaseFinding[];
  focusId?: string | null;
}) {
  const [expandedGroups, setExpandedGroups] = useState<string[]>(() =>
    groupsHolding(findings, focusId),
  );
  const groups = groupCaseFindings(findings);

  useEffect(() => {
    if (!focusId) return;
    const frame = requestAnimationFrame(() =>
      document.getElementById(`finding-${focusId}`)?.scrollIntoView?.({ block: "start" }),
    );
    return () => cancelAnimationFrame(frame);
  }, [focusId]);

  if (groups.length === 0) {
    return <p className="py-6 text-sm text-ink-muted">No findings in this analysis.</p>;
  }

  return (
    <div className="space-y-7 pt-6">
      {groups.map((group) => {
        const expanded = expandedGroups.includes(group.id);
        const canCollapse = group.collapsible && group.findings.length > INITIAL_FINDINGS;
        const visible =
          canCollapse && !expanded ? group.findings.slice(0, INITIAL_FINDINGS) : group.findings;
        const showClaimType = group.id !== "reported" && group.id !== "analytical_inference";
        return (
          <section
            key={group.id}
            aria-labelledby={`findings-${group.id}-heading`}
            className="scroll-mt-5"
          >
            <h3
              id={`findings-${group.id}-heading`}
              className={`text-[13px] font-semibold ${groupTitleClass[group.id] ?? "text-ink-secondary"}`}
            >
              {group.title}{" "}
              <span className="font-medium text-ink-muted">{group.findings.length}</span>
            </h3>
            <div id={`findings-${group.id}`} className="mt-1 divide-y divide-line">
              {visible.map((finding) => (
                <FindingRow
                  key={finding.id}
                  caseId={caseId}
                  finding={finding}
                  showClaimType={showClaimType}
                  {...sourceActions}
                />
              ))}
            </div>
            {canCollapse && (
              <button
                type="button"
                aria-expanded={expanded}
                aria-controls={`findings-${group.id}`}
                onClick={() =>
                  setExpandedGroups((current) =>
                    expanded ? current.filter((id) => id !== group.id) : [...current, group.id],
                  )
                }
                className="btn-ghost -ml-3 h-8"
              >
                {expanded ? "Show fewer" : `Show all ${group.findings.length}`}{" "}
                <span className="sr-only">{group.title.toLowerCase()}</span>
                <Icon
                  name="chevron"
                  className={`h-4 w-4 transition-transform ${expanded ? "rotate-180" : ""}`}
                />
              </button>
            )}
          </section>
        );
      })}
    </div>
  );
}
