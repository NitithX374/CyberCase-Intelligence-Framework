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
import { CitedPassages } from "./CitedPassages";
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
  showClaimType = false,
  ...sourceActions
}: FindingSourceActions & {
  caseId: string;
  finding: CaseFinding;
  showClaimType?: boolean;
}) {
  const number = finding.number;
  const flagged = finding.traceability.semanticSupport === "not_supported";
  const linked =
    !flagged && finding.epistemicStatus !== "not_confirmed" && finding.supportingSources.length > 0;

  return (
    <article
      id={`finding-${finding.id}`}
      aria-label={`Finding ${number}`}
      className="grid scroll-mt-5 grid-cols-[2.75rem_minmax(0,1fr)] gap-x-4 gap-y-3 border-t border-line px-6 py-5 @min-[42rem]:grid-cols-[2.75rem_minmax(0,1fr)_17rem]"
    >
      <span
        aria-hidden="true"
        className={`flex h-9 w-9 items-center justify-center rounded-[9px] text-sm font-bold tabular-nums ${
          flagged ? "bg-primary text-white" : "bg-surface-hover text-ink"
        }`}
      >
        {number}
      </span>
      <div className="min-w-0">
        <p className="text-base text-ink [overflow-wrap:anywhere]">{finding.text}</p>
        {(flagged || linked || (showClaimType && finding.claimType !== "reported")) && (
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {flagged && (
              <span className="badge-check">
                <Icon name="alert" />
                Check against the source
              </span>
            )}
            {linked && (
              <span className="badge-linked">
                <Icon name="check" />
                Linked to the source
              </span>
            )}
            {showClaimType && finding.claimType !== "reported" && (
              <span className="text-xs font-semibold text-ink-secondary">
                {claimTypeLabels[finding.claimType]}
              </span>
            )}
          </div>
        )}

        <FindingTraceability traceability={finding.traceability} text={finding.text} />

        <div className="mt-3 flex flex-wrap items-center gap-1.5">
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
              className="inline-flex h-6 items-center px-2 rounded bg-surface-nested text-xs font-mono font-medium text-ink-secondary hover:text-ink hover:bg-surface-hover transition-colors"
            >
              {techniqueId}
            </Link>
          ))}
        </div>

        {finding.epistemicStatus === "not_confirmed" && finding.unverifiedQuotes.length > 0 && (
          <div className="mt-3 space-y-1">
            {finding.unverifiedQuotes.map((item, index) => (
              <p key={`passage-${finding.id}-${index}`} className="text-sm font-semibold text-mark">
                {item.evidenceUnitId
                  ? "The source unit reference could not be resolved."
                  : "Not found word for word in the source."}
              </p>
            ))}
          </div>
        )}
      </div>
      <div className="col-start-2 min-w-0 @min-[42rem]:col-start-3 @min-[42rem]:row-start-1">
        <CitedPassages sources={finding.supportingSources} />
        <CitedPassages sources={finding.contradictingSources} conflicting />
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

  useEffect(() => {
    if (!focusId) return;
    const frame = requestAnimationFrame(() =>
      document.getElementById(`finding-${focusId}`)?.scrollIntoView?.({ block: "start" }),
    );
    return () => cancelAnimationFrame(frame);
  }, [focusId]);

  if (groups.length === 0) {
    return <p className="px-6 py-6 text-sm text-ink-muted">No findings in this analysis.</p>;
  }

  return (
    <div>
      <div
        aria-hidden="true"
        className="hidden grid-cols-[2.75rem_minmax(0,1fr)_17rem] gap-x-4 bg-surface-nested px-6 py-2.5 text-xs font-semibold tracking-[0.08em] text-ink-muted uppercase @min-[42rem]:grid"
      >
        <span>No.</span>
        <span>Finding</span>
        <span>Words in the source</span>
      </div>
      {groups.map((group) => {
        const expanded = expandedGroups.includes(group.id);
        const canCollapse = group.collapsible && group.findings.length > INITIAL_FINDINGS;
        const visible =
          canCollapse && !expanded ? group.findings.slice(0, INITIAL_FINDINGS) : group.findings;
        const showClaimType = group.id !== "reported";
        const isAlertGroup =
          group.id === "not_confirmed" ||
          group.id === "not_established" ||
          group.id === "contradicted" ||
          group.id === "unknown" ||
          group.id === "unknown_claim" ||
          group.id === "suspected";

        return (
          <section
            key={group.id}
            aria-labelledby={`findings-${group.id}-heading`}
            className="scroll-mt-5"
          >
            <div className="flex items-center justify-between border-t border-line bg-surface-nested px-6 py-2.5">
              <h3
                id={`findings-${group.id}-heading`}
                className={`text-sm font-semibold flex items-center gap-2 ${
                  groupTitleClass[group.id] ?? "text-ink-secondary"
                }`}
              >
                {group.title}{" "}
                <span
                  className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${
                    isAlertGroup
                      ? "bg-unresolved/10 text-unresolved"
                      : "bg-surface-nested text-ink-muted"
                  }`}
                >
                  {group.findings.length}
                </span>
              </h3>
            </div>
            <div id={`findings-${group.id}`}>
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
              <div className="border-t border-line px-6 py-3">
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
