import { Icon } from "@/components/common/icons";
import { readableValue } from "@/lib/case-update";
import type { UnresolvedGaps } from "./case-state-inspector-types";

interface CaseStateUnresolvedViewProps {
  gaps: UnresolvedGaps;
}

export function CaseStateUnresolvedView({
  gaps,
}: CaseStateUnresolvedViewProps) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xs font-extrabold uppercase tracking-wide text-ink">
          Current Unresolved Information
        </h3>
        <p className="mt-0.5 text-[11px] text-ink-secondary">
          Active gaps identified in the investigation requiring analyst follow-up
          or evidence.
        </p>
      </div>

      {gaps === null ? (
        <div className="rounded-xl border border-line bg-surface p-4 text-center">
          <p className="text-xs text-ink-secondary">
            No validated Gap Analysis is available.
          </p>
        </div>
      ) : gaps.length === 0 ? (
        <div className="rounded-xl border border-[#CAD8CE] bg-[#F1F5F1] p-4 text-center">
          <p className="text-xs font-bold text-[#3E5244]">
            All information gaps are resolved for this version.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {gaps.map((gap, index) => (
            <li key={`${gap.topic}:${gap.status}:${index}`}>
              <details className="group overflow-hidden rounded-xl border border-line bg-surface shadow-2xs transition-all">
                <summary className="flex cursor-pointer list-none select-none items-start justify-between gap-3 p-4 transition-colors hover:bg-surface-hover/60 marker:hidden">
                  <div className="min-w-0 flex-1">
                    <h4 className="text-xs font-extrabold text-ink transition-colors group-hover:text-primary">
                      {gap.topic}
                    </h4>
                    <p className="mt-1 text-xs leading-relaxed text-ink-secondary">
                      {gap.description}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-wide ${
                        gap.priority === "high"
                          ? "border border-red-200 bg-red-50 text-red-800"
                          : gap.priority === "medium"
                            ? "border border-amber-200 bg-amber-50 text-amber-800"
                            : "border border-line bg-surface-hover text-ink-secondary"
                      }`}
                    >
                      {gap.priority}
                    </span>
                    <span className="rounded-full border border-line bg-canvas px-1.5 py-0.5 text-[9px] font-bold uppercase text-ink-muted">
                      {readableValue(gap.status)}
                    </span>
                    <Icon
                      name="chevron"
                      className="h-3.5 w-3.5 text-ink-muted transition-transform duration-200 group-open:rotate-180"
                    />
                  </div>
                </summary>

                <div className="border-t border-line bg-[#FAFBF9] p-4 text-xs leading-5">
                  <dl className="grid gap-3">
                    {gap.reason && (
                      <div>
                        <dt className="font-extrabold text-ink">Why it matters</dt>
                        <dd className="mt-0.5 text-ink-secondary">
                          {gap.reason}
                        </dd>
                      </div>
                    )}
                    {gap.affects && (
                      <div>
                        <dt className="font-extrabold text-ink">
                          Affected conclusion
                        </dt>
                        <dd className="mt-0.5 text-ink-secondary">
                          {gap.affects}
                        </dd>
                      </div>
                    )}
                    {!gap.reason && !gap.affects && (
                      <div>
                        <dt className="font-extrabold text-ink">Gap Impact</dt>
                        <dd className="mt-0.5 text-ink-secondary">
                          This missing information impacts the certainty of threat
                          technique mapping and incident attribution.
                        </dd>
                      </div>
                    )}
                    <div className="flex flex-wrap items-center gap-2 border-t border-line/60 pt-2 text-[10.5px]">
                      <span className="font-bold text-ink">Priority:</span>
                      <span className="font-semibold text-ink-secondary capitalize">
                        {gap.priority}
                      </span>
                      <span className="text-ink-muted">·</span>
                      <span className="font-bold text-ink">Status:</span>
                      <span className="font-semibold text-ink-secondary">
                        {readableValue(gap.status)}
                      </span>
                    </div>
                  </dl>
                </div>
              </details>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
