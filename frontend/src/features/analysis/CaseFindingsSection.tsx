"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import { groupCaseFindings, claimTypeLabels } from "./overview";
import type { CaseFinding } from "@/features/analysis/types";
import type { SourceMessageRef } from "@/features/citations/types";
import { Icon } from "@/components/icons";
import { SourceCitationChip } from "@/features/citations/SourceCitationChip";
import { groupSourceRefs } from "@/features/citations/groupSourceRefs";
import { FindingTraceability } from "./FindingTraceability";

const INITIAL_FINDINGS = 5;

interface FindingSourceActions {
  onSelectSource: (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
    citationRole?: "supporting" | "conflicting",
  ) => void;
  activeSourceKey?: string | null;
}

function FindingSources({
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
  return groupSourceRefs(sources).map((source, index) => {
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
  });
}

const groupTitleClass: Record<string, string> = {
  not_established: "text-critical",
  contradicted: "text-critical",
  not_confirmed: "text-unresolved",
  suspected: "text-unresolved",
};

function FindingRow({
  caseId,
  finding,
  number,
  showClaimType = false,
  ...sourceActions
}: FindingSourceActions & {
  caseId: string;
  finding: CaseFinding;
  number: number;
  showClaimType?: boolean;
}) {
  return (
    <article
      id={`finding-${finding.id}`}
      aria-label={`Finding ${number}`}
      className="scroll-mt-5 grid grid-cols-[1.75rem_minmax(0,1fr)] gap-x-3 py-4"
    >
      <span aria-hidden="true" className="pt-1 text-right text-[13px] tabular-nums text-ink-muted">
        {number}
      </span>
      <div className="min-w-0">
        <div className="flex items-start justify-between gap-3">
          <p className="break-words text-[15px] leading-7 text-ink">{finding.text}</p>
          {showClaimType && finding.claimType !== "reported" && (
            <span className="shrink-0 pt-1 text-xs text-ink-muted">
              {finding.claimType === "analytical_inference"
                ? "Inference"
                : claimTypeLabels[finding.claimType]}
            </span>
          )}
        </div>

        <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1.5">
          <FindingTraceability traceability={finding.traceability} text={finding.text} />
          <FindingSources
            sources={finding.supportingSources}
            findingId={finding.id}
            role="supporting"
            {...sourceActions}
          />
          <FindingSources
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
              className="font-mono text-xs text-ink-secondary underline decoration-line-strong underline-offset-2 hover:text-ink"
            >
              {techniqueId}
            </Link>
          ))}
        </div>

        {finding.epistemicStatus === "not_confirmed" && finding.unverifiedQuotes.length > 0 && (
          <div className="mt-2 space-y-1 border-l-2 border-unresolved/50 pl-3">
            {finding.unverifiedQuotes.map((item, index) => (
              <p
                key={`passage-${finding.id}-${index}`}
                className="text-sm leading-6 font-medium text-unresolved"
              >
                {item.evidenceUnitId
                  ? "The source unit reference could not be resolved."
                  : "Not found word for word in the source."}
              </p>
            ))}
          </div>
        )}
      </div>
    </article>
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
  const findingNumbers = Object.fromEntries(
    groups.flatMap((group) => group.findings).map((finding, index) => [finding.id, index + 1]),
  );

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
    <div className="space-y-8 pt-6">
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
              className={`mb-1 flex items-baseline gap-2 text-[13px] font-semibold ${
                groupTitleClass[group.id] ?? "text-ink-secondary"
              }`}
            >
              {group.title}{" "}
              <span className="font-medium text-ink-muted">{group.findings.length}</span>
            </h3>
            <div id={`findings-${group.id}`} className="divide-y divide-line border-y border-line">
              {visible.map((finding) => (
                <FindingRow
                  key={finding.id}
                  caseId={caseId}
                  finding={finding}
                  number={findingNumbers[finding.id]}
                  showClaimType={showClaimType}
                  {...sourceActions}
                />
              ))}
            </div>
            {canCollapse && (
              <div className="mt-3">
                <button
                  type="button"
                  aria-expanded={expanded}
                  aria-controls={`findings-${group.id}`}
                  onClick={() =>
                    setExpandedGroups((current) =>
                      expanded ? current.filter((id) => id !== group.id) : [...current, group.id],
                    )
                  }
                  className="btn-ghost h-8"
                >
                  {expanded ? "Show fewer" : `Show all ${group.findings.length}`}{" "}
                  <span className="sr-only">{group.title.toLowerCase()}</span>
                  <Icon
                    name="chevron"
                    className={`h-4 w-4 transition-transform ${expanded ? "rotate-180" : ""}`}
                  />
                </button>
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}
