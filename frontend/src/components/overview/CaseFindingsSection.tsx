"use client";

import { useState } from "react";
import {
  type CaseFinding,
  type SourceMessageRef,
  groupCaseFindings,
  claimTypeLabels,
  epistemicStatusLabels,
} from "@/lib/case-overview";
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
  return (
    <article className="space-y-2 py-4">
      {!(finding.claimType === "reported" && finding.epistemicStatus === "reported") && (
        <p className="flex flex-wrap gap-x-2 text-[11px] text-ink-muted">
          <span>{claimTypeLabels[finding.claimType]}</span>
          <span>· {epistemicStatusLabels[finding.epistemicStatus]}</span>
        </p>
      )}
      <p className="break-words text-sm leading-7 text-ink sm:text-[15px]">{finding.text}</p>
      <SourceGroup sources={finding.supportingSources} findingId={finding.id} role="supporting" {...sourceActions} />
      <SourceGroup sources={finding.contradictingSources} findingId={finding.id} role="conflicting" {...sourceActions} />
      {(finding.reasoningSummary || finding.mitreTechniques.length > 0) && (
        <details className="group">
          <summary className="flex min-h-8 w-fit cursor-pointer list-none items-center gap-2 text-xs text-ink-secondary outline-none marker:hidden hover:text-ink focus-visible:ring-2 focus-visible:ring-primary">
            Analysis details
            <Icon name="chevron" className="h-3 w-3 transition-transform duration-150 group-open:rotate-180" />
          </summary>
          <div className="space-y-2 border-l border-line pl-3 pt-1">
            {finding.reasoningSummary && <p className="text-xs leading-6 text-ink-secondary">{finding.reasoningSummary}</p>}
            {finding.mitreTechniques.length > 0 && (
              <p className="text-[11px] leading-6 text-ink-muted">
                External cyber reference: {finding.mitreTechniques.map((technique) => `${technique.techniqueId} · ${technique.techniqueName}`).join("; ")}
              </p>
            )}
          </div>
        </details>
      )}
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
    <section aria-labelledby="overview-findings-heading" className="space-y-5">
      <WorkspaceSectionHeader
        headingId="overview-findings-heading"
        title="Case Findings"
        aside={<span className="text-xs text-ink-muted">{findings.length} total</span>}
      />
      {groups.length === 0 ? (
        <p className="text-sm text-ink-muted">No structured findings are available.</p>
      ) : (
        <div className="space-y-7">
          {groups.map((group) => {
            const expanded = expandedGroups.includes(group.id);
            const canCollapse = group.collapsible && group.findings.length > INITIAL_FINDINGS;
            const visible = canCollapse && !expanded ? group.findings.slice(0, INITIAL_FINDINGS) : group.findings;
            return (
              <section key={group.id} aria-labelledby={`findings-${group.id}-heading`} className="scroll-mt-5">
                <h3 id={`findings-${group.id}-heading`} className={`flex items-baseline gap-2 border-b pb-2 text-sm font-semibold ${group.collapsible ? "border-line text-ink-secondary" : "border-unresolved/30 text-ink"}`}>
                  {group.title}{" "}<span className="text-xs font-normal text-ink-muted">{group.findings.length}</span>
                </h3>
                <div id={`findings-${group.id}`} className="divide-y divide-line/70">
                  {visible.map((finding) => <FindingRow key={finding.id} finding={finding} {...sourceActions} />)}
                </div>
                {canCollapse && (
                  <button
                    type="button" aria-expanded={expanded} aria-controls={`findings-${group.id}`}
                    onClick={() => setExpandedGroups((current) => expanded
                      ? current.filter((id) => id !== group.id) : [...current, group.id])}
                    className="min-h-10 text-xs font-semibold underline decoration-line-strong underline-offset-4 hover:decoration-ink focus-visible:ring-2 focus-visible:ring-primary"
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
