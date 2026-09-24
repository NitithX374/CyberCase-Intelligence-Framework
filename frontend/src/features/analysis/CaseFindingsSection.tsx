"use client";

import { useState } from "react";
import { groupCaseFindings, claimTypeLabels } from "./overview";
import type { CaseFinding } from "@/features/analysis/types";
import type { SourceMessageRef } from "@/features/sources/types";
import { SourceCitationChip } from "@/features/sources/SourceCitationChip";
import { Icon } from "@/components/icons";
import { DisclosurePanel, DisclosureToggle } from "@/components/Disclosure";

const INITIAL_FINDINGS = 5;

export interface FindingSourceActions {
  onNavigateToSource?: (messageId: string) => void;
  onSelectSource?: (
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
  finding,
  showClaimType = false,
  ...sourceActions
}: FindingSourceActions & { finding: CaseFinding; showClaimType?: boolean }) {
  const [isOpen, setIsOpen] = useState(false);
  const detailsId = `finding-${finding.id}-details`;

  return (
    <article className="py-4">
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
        {finding.mitreTechniques.map((technique) => (
          <a
            key={technique.techniqueId}
            href={`#mitre-${technique.techniqueId}`}
            title={`ATT&CK ${technique.techniqueId}`}
            className="inline-flex h-6 items-center px-1 text-xs font-medium text-ink-secondary underline-offset-2 hover:text-ink hover:underline"
          >
            {technique.techniqueId}
          </a>
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
    </article>
  );
}

function SourceGroup({
  sources,
  findingId,
  role,
  onSelectSource,
  onNavigateToSource,
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
            onNavigateToSource={onNavigateToSource}
          />
        );
      })}
    </>
  );
}

export function CaseFindingsSection({
  findings,
  ...sourceActions
}: FindingSourceActions & {
  findings: CaseFinding[];
}) {
  const [expandedGroups, setExpandedGroups] = useState<string[]>([]);
  const groups = groupCaseFindings(findings);

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
