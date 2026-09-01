import type {
  MitreExplainedCard,
  TechnicalContextStatus,
} from "@/lib/case-overview";
import { StatusPill } from "@/components/common/StatusPill";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";

interface MitreExplainedSimplyProps {
  techniques: MitreExplainedCard[];
  status: TechnicalContextStatus;
  onOpenTechnicalContext?: () => void;
}

export function MitreExplainedSimply({
  techniques,
  status,
  onOpenTechnicalContext,
}: MitreExplainedSimplyProps) {
  if (status === "hidden") return null;
  if (status === "unavailable" || status === "no_matches") {
    return <TechnicalContextNotice status={status} />;
  }

  return (
    <section
      aria-labelledby="overview-mitre-heading"
      className="workspace-card p-4 sm:p-5"
    >
      <WorkspaceSectionHeader
        eyebrow="04 / OPTIONAL REFERENCE"
        headingId="overview-mitre-heading"
        title={
          <>
            External Cyber Reference
            <span className="ml-2 text-sm font-normal text-ink-secondary">
              · บริบททางเทคนิคภายนอก
            </span>
          </>
        }
        description="Shown because technical context was detected. This explains possible patterns and is not case evidence."
        aside={<StatusPill tone="external">External context</StatusPill>}
      />

      <div className="divide-y divide-line/70 pt-1">
        {techniques.map((technique) => (
          <article key={technique.techniqueId} className="space-y-2.5 py-4 first:pt-3 last:pb-1">
            <div className="flex flex-wrap items-baseline gap-2">
              <span className="rounded-full border border-mitre/25 bg-mitre/10 px-2 py-0.5 font-mono text-[10px] font-bold text-mitre">
                {technique.techniqueId}
              </span>
              <h3 className="text-sm font-bold text-ink">{technique.techniqueName}</h3>
            </div>
            {technique.description && (
              <p className="text-xs leading-relaxed text-ink-secondary">
                <strong className="font-bold text-ink">Reference meaning: </strong>
                {technique.description}
              </p>
            )}
            {technique.caseAssociationReason && (
              <p className="text-xs leading-relaxed text-ink-secondary">
                <strong className="font-bold text-ink">Why it may relate: </strong>
                {technique.caseAssociationReason}
              </p>
            )}
            {technique.linkedClaimTexts.length > 0 && (
              <p className="text-[11px] leading-relaxed text-ink-muted">
                Linked findings: {technique.linkedClaimTexts.join("; ")}
              </p>
            )}
          </article>
        ))}
      </div>

      {onOpenTechnicalContext && (
        <button
          type="button"
          onClick={onOpenTechnicalContext}
          className="mt-3 inline-flex items-center gap-1 text-xs font-bold text-mitre transition-colors hover:underline focus-visible:ring-2 focus-visible:ring-primary"
        >
          View technical context <span aria-hidden="true">→</span>
        </button>
      )}
    </section>
  );
}

function TechnicalContextNotice({
  status,
}: {
  status: "unavailable" | "no_matches";
}) {
  const unavailable = status === "unavailable";
  return (
    <section className="workspace-card p-4 sm:p-5" aria-label="External cyber reference status">
      <div className="flex items-start gap-2.5">
        <StatusPill tone="external">External reference</StatusPill>
        <div className="min-w-0">
          <h2 className="text-sm font-extrabold text-ink">
            {unavailable
              ? "External cyber reference unavailable"
              : "No supported cyber reference match"}
          </h2>
          <p className="mt-1 text-[11px] leading-relaxed text-ink-secondary">
            {unavailable
              ? "The case summary remains available. Optional technical enrichment could not be retrieved for this run."
              : "Technical context was evaluated, but no supported MITRE ATT&CK association was returned."}
          </p>
        </div>
      </div>
    </section>
  );
}
