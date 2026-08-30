import type { MitreExplainedCard } from "@/lib/case-overview";

interface MitreExplainedSimplyProps {
  techniques: MitreExplainedCard[];
  onOpenTechnicalContext?: () => void;
}

export function MitreExplainedSimply({
  techniques,
  onOpenTechnicalContext,
}: MitreExplainedSimplyProps) {
  if (techniques.length === 0) return null;

  return (
    <section aria-labelledby="overview-mitre-heading" className="space-y-3">
      {/* Section Header */}
      <div className="border-b border-line pb-2.5">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <div>
            <span className="font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase">
              05 / TECHNICAL REFERENCE
            </span>
            <h2
              id="overview-mitre-heading"
              className="text-base font-bold tracking-tight text-ink sm:text-lg"
            >
              Relevant MITRE ATT&amp;CK Context Explained{" "}
              <span className="text-sm font-normal text-ink-secondary">
                · ข้อมูลอ้างอิงเชิงเทคนิค
              </span>
            </h2>
          </div>
          <span className="text-[11px] font-medium text-[#6654A3]">
            External technical reference · Not independent incident evidence (Trust Boundary Notice)
          </span>
        </div>
      </div>

      {/* Technique Rows */}
      <div className="divide-y divide-line/60">
        {techniques.map((tech) => (
          <article
            key={tech.techniqueId}
            aria-label={`${tech.techniqueId} ${tech.techniqueName}`}
            className="py-3.5 first:pt-1 last:pb-1 space-y-1.5"
          >
            <div className="flex flex-wrap items-baseline gap-2">
              <span className="font-mono text-[11px] font-bold text-[#6654A3] bg-[#6654A3]/10 px-1.5 py-0.2 rounded border border-[#6654A3]/20">
                {tech.techniqueId}
              </span>
              <h3 className="text-sm font-bold text-ink">
                {tech.techniqueName}
              </h3>
            </div>

            {tech.description && (
              <p className="text-xs leading-relaxed text-ink-secondary">
                <strong className="font-semibold text-ink">Plain meaning: </strong>
                {tech.description}
              </p>
            )}

            {tech.caseAssociationReason && (
              <p className="text-xs leading-relaxed text-ink-secondary">
                <strong className="font-semibold text-ink">Why relevant in this case: </strong>
                {tech.caseAssociationReason}
              </p>
            )}

            {tech.linkedClaimTexts.length > 0 && (
              <p className="text-[11px] text-ink-muted">
                <span>Linked case findings: </span>
                <span className="text-ink-secondary">{tech.linkedClaimTexts.join("; ")}</span>
              </p>
            )}
          </article>
        ))}
      </div>

      {onOpenTechnicalContext && (
        <div className="pt-2">
          <button
            type="button"
            onClick={onOpenTechnicalContext}
            className="text-xs font-semibold text-[#6654A3] hover:underline inline-flex items-center gap-1"
          >
            <span>View detailed technical context · ดูบริบททางเทคนิค MITRE ATT&amp;CK ทั้งหมด</span>
            <span aria-hidden="true">→</span>
          </button>
        </div>
      )}
    </section>
  );
}
