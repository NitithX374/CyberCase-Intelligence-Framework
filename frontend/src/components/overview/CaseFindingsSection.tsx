import type { CaseFinding, SourceMessageRef } from "@/lib/case-overview";
import { StatusPill, type StatusPillTone } from "@/components/common/StatusPill";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";
import { Icon } from "@/components/common/icons";
import { EvidenceCitationChip } from "@/components/evidence/EvidenceCitationChip";

interface CaseFindingsSectionProps {
  findings: CaseFinding[];
  onNavigateToSource?: (messageId: string) => void;
  onSelectSource?: (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
    citationRole?: "supporting" | "conflicting",
  ) => void;
  activeSourceKey?: string | null;
}

export function CaseFindingsSection({
  findings,
  onNavigateToSource,
  onSelectSource,
  activeSourceKey,
}: CaseFindingsSectionProps) {
  return (
    <section aria-labelledby="overview-findings-heading" className="space-y-5">
      <WorkspaceSectionHeader
        headingId="overview-findings-heading"
        title={
          <>
            Case Findings
            <span className="ml-2 text-sm font-normal text-ink-secondary">
              · ข้อค้นพบจากสำนวน
            </span>
          </>
        }
        description="Based on submitted case material."
        aside={
          <span className="text-xs text-ink-muted">
            {findings.length} finding{findings.length === 1 ? "" : "s"}
          </span>
        }
      />

      {findings.length === 0 ? (
        <p className="py-4 text-xs text-ink-muted">No structured findings are available.</p>
      ) : (
        <div className="divide-y divide-line">
          {findings.map((finding) => (
            <FindingRow
              key={finding.id}
              finding={finding}
              onNavigateToSource={onNavigateToSource}
              onSelectSource={onSelectSource}
              activeSourceKey={activeSourceKey}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function FindingRow({
  finding,
  onNavigateToSource,
  onSelectSource,
  activeSourceKey,
}: Omit<CaseFindingsSectionProps, "findings"> & { finding: CaseFinding }) {
  const label = findingLabel(finding);

  return (
    <article className="space-y-3 py-5 first:pt-1 last:pb-1">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          {label && <StatusPill tone={label.tone}>{label.text}</StatusPill>}
          <p className={`${label ? "mt-2 " : ""}text-sm font-semibold leading-relaxed text-ink sm:text-[15px]`}>
            {finding.text}
          </p>
        </div>
      </div>

      <SourceGroup
        title="Sources"
        tone="support"
        sources={finding.supportingSources}
        findingId={finding.id}
        activeSourceKey={activeSourceKey}
        onNavigateToSource={onNavigateToSource}
        onSelectSource={onSelectSource}
      />
      <SourceGroup
        title="Conflicting sources"
        tone="conflict"
        sources={finding.contradictingSources}
        findingId={finding.id}
        activeSourceKey={activeSourceKey}
        onNavigateToSource={onNavigateToSource}
        onSelectSource={onSelectSource}
      />

      {(finding.reasoningSummary || finding.mitreTechniques.length > 0) && (
        <details className="group">
          <summary className="flex w-fit cursor-pointer list-none items-center gap-2 py-1 text-xs font-medium text-ink-secondary outline-none marker:hidden hover:text-ink focus-visible:ring-2 focus-visible:ring-primary">
            <span>Assessment details</span>
            <Icon
              name="chevron"
              className="h-3.5 w-3.5 shrink-0 text-ink-muted transition-transform duration-150 group-open:rotate-180"
            />
          </summary>
          <div className="space-y-3 pt-2">
            {finding.reasoningSummary && (
              <p className="text-xs leading-relaxed text-ink-secondary">
                {finding.reasoningSummary}
              </p>
            )}
            {finding.mitreTechniques.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-ink-muted">
                <span>External cyber reference:</span>
                {finding.mitreTechniques.map((technique) => (
                  <span
                    key={technique.techniqueId}
                    className="font-mono text-[11px] text-mitre"
                  >
                    {technique.techniqueId} · {technique.techniqueName}
                  </span>
                ))}
              </div>
            )}
          </div>
        </details>
      )}
    </article>
  );
}

interface SourceGroupProps {
  title: string;
  tone: "support" | "conflict";
  sources: SourceMessageRef[];
  findingId: string;
  activeSourceKey?: string | null;
  onNavigateToSource?: (messageId: string) => void;
  onSelectSource?: (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
    citationRole?: "supporting" | "conflicting",
  ) => void;
}

function SourceGroup({
  title,
  tone,
  sources,
  findingId,
  activeSourceKey,
  onNavigateToSource,
  onSelectSource,
}: SourceGroupProps) {
  if (sources.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-ink-muted">
      <span>{title}:</span>
      {sources.map((source, index) => {
        const sourceKey = `${tone}-${findingId}-${source.id}-${index}`;
        const isActive = sourceKey === activeSourceKey;
        return (
          <EvidenceCitationChip
            key={sourceKey}
            sourceRef={source}
            sourceKey={sourceKey}
            isActive={isActive}
            citationRole={tone === "conflict" ? "conflicting" : "supporting"}
            onSelect={onSelectSource}
            onNavigateToSource={onNavigateToSource}
          />
        );
      })}
    </div>
  );
}

function findingLabel(finding: CaseFinding): {
  text: string;
  tone: StatusPillTone;
} | null {
  if (finding.epistemicStatus === "contradicted" || finding.contradictingSources.length > 0) {
    return { text: "Conflicting evidence", tone: "attention" };
  }
  if (finding.claimType === "analytical_inference") {
    return { text: "Analytical inference", tone: "attention" };
  }
  if (finding.claimType === "reported" && finding.epistemicStatus === "reported") {
    return null;
  }
  return { text: "Not established", tone: "neutral" };
}
