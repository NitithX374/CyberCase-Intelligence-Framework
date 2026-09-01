import type { CaseFinding, SourceMessageRef } from "@/lib/case-overview";
import { StatusPill, type StatusPillTone } from "@/components/common/StatusPill";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";
import { Icon } from "@/components/common/icons";

interface CaseFindingsSectionProps {
  findings: CaseFinding[];
  onNavigateToSource?: (messageId: string) => void;
  onSelectSource?: (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
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
        eyebrow="02 / FINDINGS"
        headingId="overview-findings-heading"
        title={
          <>
            Case Findings
            <span className="ml-2 text-sm font-normal text-ink-secondary">
              · ข้อค้นพบจากสำนวน
            </span>
          </>
        }
        description="Each finding shows whether it is reported by a case source, an analytical inference, or not established."
        aside={
          <span className="rounded-full border border-line bg-surface px-2.5 py-1 text-[10px] font-bold text-ink-secondary">
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
  const sourceCount = finding.supportingSources.length + finding.contradictingSources.length;

  return (
    <article className="space-y-3 py-5 first:pt-1 last:pb-1">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <StatusPill tone={label.tone}>{label.text}</StatusPill>
          <p className="mt-2 text-sm font-semibold leading-relaxed text-ink sm:text-[15px]">
            {finding.text}
          </p>
        </div>
      </div>

      {finding.claimType === "reported" && (
        <p className="border-l-2 border-evidence/35 pl-3 text-[11px] leading-relaxed text-ink-muted">
          Reported by a case source; it does not independently verify it.
        </p>
      )}

      {(sourceCount > 0 || finding.reasoningSummary || finding.mitreTechniques.length > 0) && (
        <details className="group rounded-xl border border-line bg-surface/60">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-3.5 py-2.5 text-xs font-bold text-ink outline-none marker:hidden focus-visible:ring-2 focus-visible:ring-primary">
            <span className="flex min-w-0 items-center gap-2">
              <span>Evidence trail</span>
              <span className="font-normal text-ink-muted">
                {sourceCount > 0
                  ? `${sourceCount} source${sourceCount === 1 ? "" : "s"}`
                  : "Assessment detail"}
              </span>
            </span>
            <Icon
              name="chevron"
              className="h-3.5 w-3.5 shrink-0 text-ink-muted transition-transform duration-150 group-open:rotate-180"
            />
          </summary>
          <div className="space-y-3 border-t border-line px-3.5 py-3">
            {finding.reasoningSummary && (
              <p className="text-xs leading-relaxed text-ink-secondary">
                <strong className="font-bold text-ink">How this was assessed: </strong>
                {finding.reasoningSummary}
              </p>
            )}
            <SourceGroup
              title="Supporting case sources"
              tone="support"
              sources={finding.supportingSources}
              findingId={finding.id}
              activeSourceKey={activeSourceKey}
              onNavigateToSource={onNavigateToSource}
              onSelectSource={onSelectSource}
            />
            <SourceGroup
              title="Conflicting case sources"
              tone="conflict"
              sources={finding.contradictingSources}
              findingId={finding.id}
              activeSourceKey={activeSourceKey}
              onNavigateToSource={onNavigateToSource}
              onSelectSource={onSelectSource}
            />
            {finding.mitreTechniques.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-ink-muted">
                <span>External cyber reference:</span>
                {finding.mitreTechniques.map((technique) => (
                  <span
                    key={technique.techniqueId}
                    className="rounded-full border border-mitre/25 bg-mitre/10 px-2 py-0.5 font-mono text-[10px] font-bold text-mitre"
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
          <button
            key={sourceKey}
            type="button"
            aria-expanded={isActive}
            onClick={(event) => {
              if (onSelectSource) {
                onSelectSource(source, event.currentTarget, sourceKey);
              } else {
                onNavigateToSource?.(source.id);
              }
            }}
            className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 font-medium transition-colors focus-visible:ring-2 focus-visible:ring-primary ${
              isActive
                ? "border-primary bg-primary text-ivory"
                : tone === "conflict"
                  ? "border-unresolved/30 bg-unresolved/10 text-unresolved hover:border-unresolved"
                  : "border-line bg-surface text-ink-secondary hover:border-ink hover:text-ink"
            }`}
          >
            {source.label}
            <span aria-hidden="true">↗</span>
          </button>
        );
      })}
    </div>
  );
}

function findingLabel(finding: CaseFinding): {
  text: string;
  tone: StatusPillTone;
} {
  if (finding.epistemicStatus === "contradicted" || finding.contradictingSources.length > 0) {
    return { text: "Conflicting evidence", tone: "attention" };
  }
  if (finding.claimType === "analytical_inference") {
    return { text: "Analytical inference", tone: "attention" };
  }
  if (finding.claimType === "reported" && finding.epistemicStatus === "reported") {
    return { text: "Reported in case material", tone: "evidence" };
  }
  return { text: "Not established", tone: "neutral" };
}
