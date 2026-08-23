import type { InvestigationPoint } from "@/lib/case-overview";

interface InvestigationPointsSectionProps {
  points: InvestigationPoint[];
}

export function InvestigationPointsSection({
  points,
}: InvestigationPointsSectionProps) {
  if (points.length === 0) return null;

  return (
    <section aria-labelledby="overview-investigation-points-heading" className="space-y-3">
      <div className="border-b border-line pb-2.5">
        <span className="font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase">
          06 / INVESTIGATION POINTS
        </span>
        <h2
          id="overview-investigation-points-heading"
          className="text-base font-bold tracking-tight text-ink sm:text-lg"
        >
          Points for Further Investigation{" "}
          <span className="text-sm font-normal text-ink-secondary">
            · แนวทางแสวงหาพยานหลักฐานเพิ่มเติม
          </span>
        </h2>
        <p className="mt-0.5 text-xs text-ink-secondary">
          Practical investigative considerations to substantiate unconfirmed details.
        </p>
      </div>

      <div className="divide-y divide-line/60">
        {points.map((point, index) => (
          <article
            key={point.id}
            className="py-3.5 first:pt-1 last:pb-1 flex items-baseline gap-3 sm:gap-4"
          >
            <span className="font-mono text-xs font-bold text-ink-muted shrink-0 w-6">
              {String(index + 1).padStart(2, "0")}
            </span>

            <div className="min-w-0 flex-1 space-y-0.5">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <p className="text-xs font-bold leading-relaxed text-ink sm:text-sm">
                  {point.suggestion}
                </p>
                {point.priority === "high" && (
                  <span className="font-mono text-[9.5px] font-bold uppercase text-red-700 shrink-0">
                    High Priority
                  </span>
                )}
              </div>

              {point.rationale && (
                <p className="text-xs text-ink-secondary leading-relaxed">
                  <span className="text-ink-muted">Rationale: </span>
                  {point.rationale}
                </p>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
