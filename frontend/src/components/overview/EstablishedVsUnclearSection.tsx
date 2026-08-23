import type { EstablishedFact, SourceMessageRef, UnclearItem } from "@/lib/case-overview";

interface EstablishedVsUnclearSectionProps {
  establishedFacts: EstablishedFact[];
  unclearItems: UnclearItem[];
  onNavigateToSource?: (messageId: string) => void;
  onSelectSource?: (
    sourceRef: SourceMessageRef,
    anchorEl: HTMLElement,
    sourceKey: string,
  ) => void;
  activeSourceKey?: string | null;
  onOpenMaterials?: () => void;
}

export function EstablishedVsUnclearSection({
  establishedFacts,
  unclearItems,
  onNavigateToSource,
  onSelectSource,
  activeSourceKey,
  onOpenMaterials,
}: EstablishedVsUnclearSectionProps) {
  return (
    <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
      {/* 3. Established from the Case */}
      <section aria-labelledby="overview-established-heading" className="space-y-3">
        <div className="border-b border-line pb-2.5">
          <span className="font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase">
            03 / ESTABLISHED
          </span>
          <h2
            id="overview-established-heading"
            className="text-base font-bold tracking-tight text-ink sm:text-lg"
          >
            What is Established? <span className="text-sm font-normal text-ink-secondary">· ข้อมูลที่ยืนยันได้</span>
          </h2>
          <p className="mt-0.5 text-xs text-ink-secondary">
            Facts directly supported by submitted case evidence.
          </p>
        </div>

        {establishedFacts.length === 0 ? (
          <p className="py-4 text-xs text-ink-muted">
            No specific evidence-backed claims recorded yet.
          </p>
        ) : (
          <div className="divide-y divide-line/50">
            {establishedFacts.map((fact) => (
              <div key={fact.id} className="flex items-start gap-2.5 py-3 first:pt-1 last:pb-1">
                <span
                  aria-hidden="true"
                  className="mt-0.5 text-xs font-bold text-emerald-700"
                >
                  ✓
                </span>
                <div className="min-w-0 flex-1 space-y-1">
                  <p className="text-xs font-semibold leading-relaxed text-ink sm:text-[13px]">
                    {fact.text}
                  </p>
                  {fact.sourceMessages.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-ink-muted">
                      <span>Source —</span>
                      {fact.sourceMessages.map((src, srcIdx) => {
                        const sourceKey = `established-${fact.id}-${src.id}-${srcIdx}`;
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
                            className={`font-medium inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] transition-all duration-150 ${
                              isActive
                                ? "bg-primary text-ivory font-bold shadow-xs ring-2 ring-primary/20"
                                : "text-ink-secondary hover:text-ink hover:bg-surface-nested hover:underline focus-visible:ring-1 focus-visible:ring-primary"
                            }`}
                            title={`Inspect source evidence: ${src.sourceTypeLabel}`}
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
            ))}
            {onOpenMaterials && (
              <div className="pt-2">
                <button
                  type="button"
                  onClick={onOpenMaterials}
                  className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1"
                >
                  <span>View all in Case Materials · ดูข้อมูลสำนวนทั้งหมด</span>
                  <span aria-hidden="true">→</span>
                </button>
              </div>
            )}
          </div>
        )}
      </section>

      {/* 4. What Remains Unclear */}
      <section aria-labelledby="overview-unclear-heading" className="space-y-3">
        <div className="border-b border-line pb-2.5">
          <span className="font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase">
            04 / STILL UNCLEAR
          </span>
          <h2
            id="overview-unclear-heading"
            className="text-base font-bold tracking-tight text-ink sm:text-lg"
          >
            What Remains Unclear? <span className="text-sm font-normal text-ink-secondary">· ประเด็นที่ยังไม่ชัดเจน</span>
          </h2>
          <p className="mt-0.5 text-xs text-ink-secondary">
            Information gaps and unconfirmed points requiring additional evidence.
          </p>
        </div>

        {unclearItems.length === 0 ? (
          <p className="py-4 text-xs text-ink-muted">
            No unresolved information gaps identified for this case.
          </p>
        ) : (
          <div className="divide-y divide-line/50">
            {unclearItems.map((item) => (
              <div key={item.id} className="flex items-start gap-2.5 py-3 first:pt-1 last:pb-1">
                <span
                  aria-hidden="true"
                  className="mt-0.5 text-xs font-bold text-amber-700"
                >
                  ?
                </span>
                <div className="min-w-0 flex-1 space-y-1">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <p className="text-xs font-semibold leading-relaxed text-ink sm:text-[13px]">
                      {item.description}
                    </p>
                    {item.priority === "high" && (
                      <span className="font-mono text-[9.5px] font-bold uppercase text-red-700 shrink-0">
                        High Priority
                      </span>
                    )}
                  </div>
                  {item.reason && item.reason !== item.description && (
                    <p className="text-[11px] text-ink-secondary">
                      {item.reason}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
