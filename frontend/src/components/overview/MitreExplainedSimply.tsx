import type {
  MitreExplainedCard,
  TechnicalContextStatus,
} from "@/lib/case-overview";
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
      className="border-t border-line pt-4"
    >
      <WorkspaceSectionHeader
        headingId="overview-mitre-heading"
        title="External Cyber Reference"
        description="MITRE ATT&CK patterns associated with these findings."
      />

      <div className="divide-y divide-line/70 pt-1">
        {techniques.map((technique) => (
          <article key={technique.techniqueId} className="space-y-2.5 py-4 first:pt-3 last:pb-1">
            <div className="flex flex-wrap items-baseline gap-2">
              <span className="font-mono text-[11px] text-mitre">
                {technique.techniqueId}
              </span>
              <h3 className="text-sm font-bold text-ink">{technique.techniqueName}</h3>
            </div>
            {technique.description && (
              <p className="text-xs leading-relaxed text-ink-secondary">
                {technique.description}
              </p>
            )}
            {technique.caseAssociationReason && (
              <p className="text-xs leading-relaxed text-ink-secondary">
                {technique.caseAssociationReason}
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
    <section className="border-t border-line pt-4" aria-label="External cyber reference status">
      <div className="flex items-start gap-2.5">
        <div className="min-w-0">
          <h2 className="text-sm font-extrabold text-ink">
            {unavailable
              ? "External cyber reference unavailable"
              : "No supported cyber reference match"}
          </h2>
          <p className="mt-1 text-[11px] leading-relaxed text-ink-secondary">
            {unavailable
              ? "Technical references could not be retrieved."
              : "No MITRE ATT&CK associations were found."}
          </p>
        </div>
      </div>
    </section>
  );
}
