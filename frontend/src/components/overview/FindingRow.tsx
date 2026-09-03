import type { CaseFinding, SourceMessageRef } from "@/lib/case-overview";
import { claimTypeLabels, epistemicStatusLabels } from "@/lib/case-finding-groups";
import { EvidenceCitationChip } from "@/components/evidence/EvidenceCitationChip";
import { Icon } from "@/components/common/icons";

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
