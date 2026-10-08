"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import { groupCaseFindings, claimTypeLabels } from "./overview";
import type { CaseFinding, QuotePlace } from "@/features/analysis/types";
import type { SourceMessageRef } from "@/features/citations/types";
import { Icon } from "@/components/icons";
import { DisclosurePanel, DisclosureToggle } from "@/components/Disclosure";
import { SourceCitationChip } from "@/features/citations/SourceCitationChip";
import { groupSourceRefs } from "@/features/citations/groupSourceRefs";
import { FindingTraceability } from "./FindingTraceability";

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

export function FindingSources({
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
  const [isOpen, setIsOpen] = useState(false);
  const detailsId = `finding-${finding.id}-details`;
  const isSupported = finding.traceability.semanticSupport === "supported";

  const isUnknown = finding.claimType === "unknown" || finding.epistemicStatus === "unknown";
  const isNotConfirmed = finding.epistemicStatus === "not_confirmed";
  const isContradicted =
    finding.epistemicStatus === "contradicted" || finding.epistemicStatus === "not_established";

  return (
    <article
      id={`finding-${finding.id}`}
      aria-label={`Finding ${number}`}
      className={`scroll-mt-5 rounded-xl border p-4 sm:p-5 transition-all duration-150 ${
        isSupported ? "border-l-4 border-l-established" : ""
      } ${
        isNotConfirmed
          ? "border-unresolved/30 bg-surface shadow-xs"
          : isUnknown
            ? "border-amber-500/25 bg-amber-500/[0.02] dark:bg-amber-500/[0.04] shadow-xs"
            : isContradicted
              ? "border-critical/30 bg-critical/[0.02] shadow-xs"
              : isSupported
                ? "border-established/30 bg-accent-soft/40 shadow-xs"
                : "border-line bg-surface hover:border-line-strong hover:shadow-xs"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <span
          aria-hidden="true"
          className={`inline-flex h-7 min-w-7 shrink-0 items-center justify-center rounded-full px-2 text-xs font-semibold tabular-nums ${
            isSupported
              ? "bg-established/10 text-established"
              : "bg-surface-nested text-ink-secondary"
          }`}
        >
          {number}
        </span>
        <p className="break-words text-[15px] sm:text-[16px] font-medium leading-relaxed text-ink flex-1 tracking-tight">
          {finding.text}
        </p>
        <div className="flex items-center gap-1.5 shrink-0">
          {showClaimType && finding.claimType !== "reported" && (
            <span
              className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${
                finding.claimType === "unknown"
                  ? "bg-amber-500/10 text-amber-700 dark:text-amber-400"
                  : "bg-surface-nested text-ink-secondary"
              }`}
            >
              {finding.claimType === "analytical_inference"
                ? "Inference"
                : claimTypeLabels[finding.claimType]}
            </span>
          )}
        </div>
      </div>

      <FindingTraceability traceability={finding.traceability} text={finding.text} />

      <div className="mt-3 flex flex-wrap items-center gap-1.5 pt-2.5 border-t border-line/60">
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
        <DisclosurePanel
          id={detailsId}
          className="mt-3 rounded-lg border border-line bg-surface-nested p-3.5 text-[13px] leading-relaxed text-ink-secondary"
        >
          <div className="text-[11px] font-semibold uppercase tracking-wider text-ink-muted mb-1">
            Reasoning & Analysis
          </div>
          {finding.reasoningSummary}
        </DisclosurePanel>
      )}

      {finding.epistemicStatus === "not_confirmed" && finding.unverifiedQuotes.length > 0 && (
        <div className="mt-3 space-y-2 rounded-lg border border-unresolved/20 bg-unresolved/5 p-3.5 text-sm">
          {finding.unverifiedQuotes.map((item, index) => {
            const key = `passage-${finding.id}-${index}`;
            const passage = item.passage;
            const meaning = item.meaningPassage;
            return (
              <div key={key} className="text-sm leading-6 text-ink-secondary">
                <p className="font-medium text-unresolved">
                  {item.evidenceUnitId
                    ? "The source unit reference could not be resolved."
                    : "Not found word for word in the source."}
                </p>
                {item.places.map((place, placeIndex) => (
                  <p key={placeIndex} className="text-xs text-ink-muted mt-0.5">
                    {placeText(place)}
                  </p>
                ))}
                {passage && (
                  <button
                    type="button"
                    aria-haspopup="dialog"
                    onClick={(event) =>
                      sourceActions.onSelectSource(passage, event.currentTarget, key)
                    }
                    className="mt-1 text-xs font-medium text-ink underline underline-offset-2 hover:text-ink-secondary inline-block"
                  >
                    Show in source
                  </button>
                )}
                {meaning && (
                  <p className="mt-1 text-xs">
                    {meaning.quoteLabel}{" "}
                    <button
                      type="button"
                      aria-haspopup="dialog"
                      onClick={(event) =>
                        sourceActions.onSelectSource(meaning, event.currentTarget, `${key}-meaning`)
                      }
                      className="font-medium text-ink underline underline-offset-2 hover:text-ink-secondary"
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
            <div className="flex items-center justify-between mb-3">
              <h3
                id={`findings-${group.id}-heading`}
                className={`text-[13px] font-semibold flex items-center gap-2 ${
                  groupTitleClass[group.id] ?? "text-ink-secondary"
                }`}
              >
                {group.title}{" "}
                <span
                  className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                    isAlertGroup
                      ? "bg-unresolved/10 text-unresolved"
                      : "bg-surface-nested text-ink-muted"
                  }`}
                >
                  {group.findings.length}
                </span>
              </h3>
            </div>
            <div id={`findings-${group.id}`} className="space-y-3">
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
