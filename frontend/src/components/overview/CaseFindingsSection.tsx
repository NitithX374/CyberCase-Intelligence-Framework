"use client";

import { useState } from "react";
import {
  groupCaseFindings,
  claimTypeLabels,
  epistemicStatusLabels,
} from "@/lib/caseOverview";
import type { CaseFinding, SourceMessageRef } from "@/lib/caseOverviewTypes";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";
import { EvidenceCitationChip } from "@/components/evidence/EvidenceCitationChip";
import { Icon } from "@/components/common/icons";

const INITIAL_FINDINGS = 5;

export interface FindingSourceActions {
  onNavigateToSource?: (messageId: string) => void;
  onSelectSource?: (
    sourceRef: SourceMessageRef, anchorElement: HTMLElement, sourceKey: string,
    citationRole?: "supporting" | "conflicting",
  ) => void;
  activeSourceKey?: string | null;
}

export function FindingRow({ finding, ...sourceActions }: FindingSourceActions & { finding: CaseFinding }) {
  const isReportedDefault = finding.claimType === "reported" && finding.epistemicStatus === "reported";

  const getBadgeStyle = (status: string) => {
    switch (status) {
      case "not_established":
        return "bg-danger/10 text-danger border border-danger/20";
      case "not_confirmed":
      case "suspected":
        return "bg-unresolved/15 text-unresolved border border-unresolved/25";
      case "contradicted":
        return "bg-critical/10 text-critical border border-critical/20";
      case "reported":
      default:
        return "bg-surface-nested text-ink-secondary border border-line";
    }
  };

  return (
    <article className="grid min-w-[640px] grid-cols-[10rem_minmax(0,1fr)_minmax(12rem,0.7fr)] gap-4 px-4 py-3.5 items-start hover:bg-surface-hover/30 transition-colors">
      <div className="min-w-0 space-y-1">
        {!isReportedDefault ? (
          <div className="space-y-1">
            <span className={`inline-flex rounded px-2 py-0.5 text-[10px] font-bold tracking-tight ${getBadgeStyle(finding.epistemicStatus)}`}>
              {epistemicStatusLabels[finding.epistemicStatus]}
            </span>
            <p className="flex flex-wrap items-center gap-x-1 text-[11px] leading-tight text-ink-muted">
              <span>{claimTypeLabels[finding.claimType]}</span>
              <span>· {epistemicStatusLabels[finding.epistemicStatus]}</span>
            </p>
          </div>
        ) : (
          <span className="inline-flex rounded border border-line bg-surface-nested px-2 py-0.5 text-[10px] font-semibold text-ink-secondary">
            Reported
          </span>
        )}
      </div>
      <div className="min-w-0 space-y-2">
        <p className="break-words text-xs sm:text-sm leading-relaxed text-ink">{finding.text}</p>
        {(finding.reasoningSummary || finding.mitreTechniques.length > 0) && (
          <details className="group rounded border border-line/60 bg-surface-nested/40 p-2.5 text-xs">
            <summary className="flex min-h-6 w-fit cursor-pointer list-none items-center gap-1.5 font-medium text-ink-secondary outline-none marker:hidden hover:text-ink focus-visible:ring-1 focus-visible:ring-primary">
              <Icon name="chevron" className="h-3 w-3 transition-transform duration-150 group-open:rotate-180" />
              <span>Analysis details</span>
            </summary>
            <div className="mt-2 space-y-1.5 border-t border-line/60 pt-2">
              {finding.reasoningSummary && <p className="leading-relaxed text-ink-secondary">{finding.reasoningSummary}</p>}
              {finding.mitreTechniques.length > 0 && (
                <p className="text-[11px] leading-relaxed text-ink-muted">
                  <span className="font-semibold text-mitre">External cyber reference: </span>
                  {finding.mitreTechniques.map((technique) => `${technique.techniqueId} · ${technique.techniqueName}`).join("; ")}
                </p>
              )}
            </div>
          </details>
        )}
      </div>
      <div className="min-w-0 space-y-1.5">
        <SourceGroup sources={finding.supportingSources} findingId={finding.id} role="supporting" {...sourceActions} />
        <SourceGroup sources={finding.contradictingSources} findingId={finding.id} role="conflicting" {...sourceActions} />
      </div>
    </article>
  );
}

function SourceGroup({ sources, findingId, role, onSelectSource, onNavigateToSource, activeSourceKey }: FindingSourceActions & {
  sources: SourceMessageRef[];
  findingId: string;
  role: "supporting" | "conflicting";
}) {
  if (!sources.length) return null;
  return (
    <div className="flex flex-col items-start gap-1">
      {sources.map((source, index) => {
        const key = `${role}-${findingId}-${source.id}-${index}`;
        return <EvidenceCitationChip key={key} sourceRef={source} sourceKey={key} citationRole={role}
          showDocumentName isActive={activeSourceKey === key} onSelect={onSelectSource} onNavigateToSource={onNavigateToSource} />;
      })}
    </div>
  );
}

export function CaseFindingsSection({ findings, ...sourceActions }: FindingSourceActions & {
  findings: CaseFinding[];
}) {
  const [expandedGroups, setExpandedGroups] = useState<string[]>([]);
  const groups = groupCaseFindings(findings);

  return (
    <section aria-labelledby="overview-findings-heading" className="space-y-4">
      <WorkspaceSectionHeader
        headingId="overview-findings-heading"
        title="Case Findings"
        aside={<span className="text-xs text-ink-muted">{findings.length} total</span>}
      />
      {groups.length === 0 ? (
        <p className="text-sm text-ink-muted">No structured findings are available.</p>
      ) : (
        <div className="space-y-6">
          {groups.map((group) => {
            const expanded = expandedGroups.includes(group.id);
            const canCollapse = group.collapsible && group.findings.length > INITIAL_FINDINGS;
            const visible = canCollapse && !expanded ? group.findings.slice(0, INITIAL_FINDINGS) : group.findings;
            return (
              <section key={group.id} aria-labelledby={`findings-${group.id}-heading`} className="scroll-mt-5 space-y-2">
                <h3 id={`findings-${group.id}-heading`} className={`flex items-baseline gap-2 text-sm font-semibold ${group.collapsible ? "text-ink-secondary" : "text-ink"}`}>
                  {group.title}{" "}<span className="text-xs font-normal text-ink-muted">{group.findings.length}</span>
                </h3>
                <div className="overflow-x-auto rounded-lg border border-line bg-surface shadow-xs">
                  <div className="grid min-w-[640px] grid-cols-[10rem_minmax(0,1fr)_minmax(12rem,0.7fr)] gap-4 border-b border-line bg-surface-nested px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
                    <span>Assessment</span>
                    <span>Finding &amp; Details</span>
                    <span>Evidence</span>
                  </div>
                  <div id={`findings-${group.id}`} className="divide-y divide-line/60">
                    {visible.map((finding) => <FindingRow key={finding.id} finding={finding} {...sourceActions} />)}
                  </div>
                </div>
                {canCollapse && (
                  <button
                    type="button" aria-expanded={expanded} aria-controls={`findings-${group.id}`}
                    onClick={() => setExpandedGroups((current) => expanded
                      ? current.filter((id) => id !== group.id) : [...current, group.id])}
                    className="min-h-8 text-xs font-semibold underline decoration-line-strong underline-offset-4 hover:decoration-ink focus-visible:ring-2 focus-visible:ring-primary"
                  >
                    {expanded ? "Show fewer" : `Show all ${group.findings.length}`} {group.title.toLowerCase()}
                  </button>
                )}
              </section>
            );
          })}
        </div>
      )}
    </section>
  );
}
