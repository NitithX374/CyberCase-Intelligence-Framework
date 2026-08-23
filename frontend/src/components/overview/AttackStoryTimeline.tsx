import type { AttackStoryStep, SourceMessageRef } from "@/lib/case-overview";

interface AttackStoryTimelineProps {
  steps: AttackStoryStep[];
  onNavigateToSource?: (messageId: string) => void;
  onSelectSource?: (
    sourceRef: SourceMessageRef,
    anchorEl: HTMLElement,
    sourceKey: string,
  ) => void;
  activeSourceKey?: string | null;
}

export function AttackStoryTimeline({
  steps,
  onNavigateToSource,
  onSelectSource,
  activeSourceKey,
}: AttackStoryTimelineProps) {
  if (steps.length === 0) return null;

  return (
    <section aria-labelledby="overview-attack-story-heading" className="space-y-3">
      <div className="border-b border-line pb-2.5">
        <span className="font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase">
          02 / PROGRESSION
        </span>
        <h2
          id="overview-attack-story-heading"
          className="text-base font-bold tracking-tight text-ink sm:text-lg"
        >
          Attack Story &amp; Progression <span className="text-sm font-normal text-ink-secondary">· ลำดับเหตุการณ์</span>
        </h2>
        <p className="mt-0.5 text-xs text-ink-secondary">
          Incident sequence derived from reported case evidence and findings.
        </p>
      </div>

      <div className="divide-y divide-line/60">
        {steps.map((step) => {
          const isReported =
            step.claimType === "reported" || step.epistemicStatus === "reported";
          const isSuspected =
            step.epistemicStatus === "suspected" ||
            step.epistemicStatus === "not_confirmed" ||
            step.epistemicStatus === "unknown";
          const isContradicted = step.epistemicStatus === "contradicted";

          return (
            <article
              key={step.stepNumber}
              aria-label={`Step ${step.stepNumber}: ${step.text}`}
              className="py-3.5 first:pt-1 last:pb-1"
            >
              <div className="flex items-baseline gap-3 sm:gap-4">
                <span className="font-mono text-xs font-bold text-ink-muted shrink-0 w-6">
                  {String(step.stepNumber).padStart(2, "0")}
                </span>

                <div className="min-w-0 flex-1 space-y-1.5">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <p className="text-sm font-semibold leading-relaxed text-ink">
                      {step.text}
                    </p>
                    <span className="text-[10px] font-medium text-ink-muted shrink-0">
                      {isReported
                        ? "Reported in case"
                        : isContradicted
                          ? "Contradicted"
                          : isSuspected
                            ? "Unconfirmed"
                            : "Analytical interpretation"}
                    </span>
                  </div>

                  {/* Linked MITRE Techniques inline */}
                  {step.mitreTechniques.length > 0 && (
                    <div className="space-y-1 pt-0.5">
                      {step.mitreTechniques.map((tech) => (
                        <div
                          key={tech.techniqueId}
                          className="flex flex-wrap items-baseline gap-2 text-xs"
                        >
                          <span className="font-mono text-[10.5px] font-bold text-[#6654A3] bg-[#6654A3]/10 px-1.5 py-0.2 rounded border border-[#6654A3]/20">
                            {tech.techniqueId} · {tech.techniqueName}
                          </span>
                          {tech.reason && (
                            <span className="text-ink-secondary text-[11.5px]">
                              {tech.reason}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Source Traceability */}
                  {step.sourceMessages.length > 0 && (
                    <div className="flex flex-wrap items-center gap-2 pt-0.5 text-xs text-ink-muted">
                      <span>Source:</span>
                      {step.sourceMessages.map((src, srcIdx) => {
                        const sourceKey = `step-${step.stepNumber}-${src.id}-${srcIdx}`;
                        const isActive = activeSourceKey === sourceKey;
                        return (
                          <button
                            key={src.id}
                            type="button"
                            aria-expanded={isActive}
                            onClick={(e) => {
                              if (onSelectSource) {
                                onSelectSource(src, e.currentTarget, sourceKey);
                              } else {
                                onNavigateToSource?.(src.id);
                              }
                            }}
                            title={`Inspect source evidence: ${src.sourceTypeLabel}`}
                            className={`font-medium inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-xs transition-all duration-150 ${
                              isActive
                                ? "bg-primary text-ivory font-bold shadow-xs ring-2 ring-primary/20"
                                : "text-ink-secondary hover:text-ink hover:bg-surface-nested hover:underline focus-visible:ring-1 focus-visible:ring-primary"
                            }`}
                          >
                            <span>{src.label}</span>
                            <span className={isActive ? "text-ivory font-bold" : "text-ink-muted"}>↗</span>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
