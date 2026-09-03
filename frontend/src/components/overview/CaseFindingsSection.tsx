"use client";

import { useState } from "react";
import type { CaseFinding } from "@/lib/case-overview";
import { groupCaseFindings } from "@/lib/case-finding-groups";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";
import { FindingRow, type FindingSourceActions } from "./FindingRow";

const INITIAL_FINDINGS = 5;

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
