"use client";

import { useState } from "react";
import { Icon } from "@/components/common/icons";
import {
  formatCaseUpdateValue,
  readableValue,
  type CaseUpdateView,
} from "@/lib/case-update";
import type { MitreCandidateView } from "@/lib/mitre-candidate";

export interface CaseStateInspectorUpdate {
  ordinal: number;
  update: CaseUpdateView;
  mitreCandidates?: MitreCandidateView[] | null;
}

type InspectorTab = "delta" | "unresolved" | "mitre";

interface CaseStateInspectorProps {
  updates: CaseStateInspectorUpdate[];
  selectedOrdinal: number | null;
  onSelectOrdinal: (ordinal: number) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function CaseStateInspector({
  updates,
  selectedOrdinal,
  onSelectOrdinal,
  isOpen,
  onClose,
}: CaseStateInspectorProps) {
  const [activeTab, setActiveTab] = useState<InspectorTab>("delta");

  if (!isOpen) return null;

  const currentItem =
    updates.find((u) => u.ordinal === selectedOrdinal) ??
    updates[updates.length - 1] ??
    null;

  const unresolvedGaps =
    currentItem?.update.currentUnresolvedInformation ?? null;
  const unresolvedCount = unresolvedGaps?.length ?? 0;
  const mitreCandidates = currentItem?.mitreCandidates ?? null;
  const mitreCount = mitreCandidates?.length ?? 0;

  const isUpdated =
    currentItem?.update.status === "updated" &&
    currentItem.update.childVersion !== null;

  return (
    <>
      {/* Mobile backdrop */}
      <div
        role="presentation"
        className="fixed inset-0 z-30 bg-black/20 backdrop-blur-xs lg:hidden"
        onClick={onClose}
      />

      <aside
        aria-label="Case State Inspector"
        className="fixed inset-y-0 right-0 z-40 flex h-full w-full max-w-md flex-col border-l border-line bg-canvas shadow-xl transition-all lg:static lg:z-auto lg:h-full lg:w-[380px] xl:w-[420px] lg:shadow-none"
      >
        {/* Full-ceiling Top Header */}
        <div className="flex min-h-[76px] shrink-0 items-center justify-between border-b border-line bg-canvas px-4 py-3 sm:px-5 md:min-h-[72px]">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-surface-hover text-ink">
              <Icon name="details" className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <h2 className="truncate text-xs font-extrabold uppercase tracking-wider text-ink">
                Case State Inspector
              </h2>
              <p className="truncate text-[10px] text-ink-muted">
                {updates.length > 0
                  ? `${updates.length} state update${updates.length > 1 ? "s" : ""}`
                  : "Live delta, gaps & MITRE mapping"}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close Case State Inspector"
            title="Close inspector"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-ink-secondary transition-colors hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-primary outline-none cursor-pointer"
          >
            <Icon name="close" className="h-4 w-4" />
          </button>
        </div>

        {/* History Switcher Tabs (when multiple updates exist) */}
        {updates.length > 1 && (
          <div className="flex shrink-0 items-center gap-1.5 overflow-x-auto border-b border-line bg-surface/50 px-4 py-2">
            <span className="shrink-0 text-[10px] font-bold text-ink-muted mr-1">
              History:
            </span>
            {updates.map((item) => {
              const isSelected = currentItem?.ordinal === item.ordinal;
              const itemIsUpdated =
                item.update.status === "updated" &&
                item.update.childVersion !== null;
              const label = itemIsUpdated
                ? `V${item.update.parentVersion} → V${item.update.childVersion}`
                : `V${item.update.parentVersion}`;

              return (
                <button
                  key={item.ordinal}
                  type="button"
                  onClick={() => onSelectOrdinal(item.ordinal)}
                  className={`shrink-0 rounded-lg px-2.5 py-1 text-[11px] font-bold transition-colors cursor-pointer ${
                    isSelected
                      ? "bg-primary text-ivory shadow-xs"
                      : "border border-line bg-surface text-ink-secondary hover:border-primary hover:text-ink"
                  }`}
                >
                  #{item.ordinal} {label}
                </button>
              );
            })}
          </div>
        )}

        {/* Sub-view Navigation Tabs: State Delta vs Current Unresolved vs MITRE Candidates */}
        <div className="flex shrink-0 border-b border-line bg-canvas px-3 py-2 sm:px-4">
          <div className="flex w-full gap-1 rounded-xl bg-surface-hover p-1">
            <button
              type="button"
              onClick={() => setActiveTab("delta")}
              className={`flex-1 rounded-lg py-1.5 text-center text-[11px] font-bold transition-all cursor-pointer ${
                activeTab === "delta"
                  ? "bg-surface text-ink shadow-xs"
                  : "text-ink-secondary hover:text-ink"
              }`}
            >
              State Delta
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("unresolved")}
              className={`flex flex-1 items-center justify-center gap-1 rounded-lg py-1.5 text-center text-[11px] font-bold transition-all cursor-pointer ${
                activeTab === "unresolved"
                  ? "bg-surface text-ink shadow-xs"
                  : "text-ink-secondary hover:text-ink"
              }`}
            >
              <span>Unresolved</span>
              {unresolvedCount > 0 && (
                <span className="rounded-full bg-red-100 px-1.5 py-0.2 text-[9px] font-extrabold text-red-800">
                  {unresolvedCount}
                </span>
              )}
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("mitre")}
              className={`flex flex-1 items-center justify-center gap-1 rounded-lg py-1.5 text-center text-[11px] font-bold transition-all cursor-pointer ${
                activeTab === "mitre"
                  ? "bg-surface text-ink shadow-xs"
                  : "text-ink-secondary hover:text-ink"
              }`}
            >
              <span>MITRE</span>
              {mitreCount > 0 && (
                <span className="rounded-full bg-[#EDE9F2] px-1.5 py-0.2 text-[9px] font-extrabold text-[#51495D]">
                  {mitreCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Tab Content Body */}
        <div className="min-h-0 flex-1 overflow-y-auto p-4 sm:p-5">
          {!currentItem ? (
            <div className="flex h-full min-h-[300px] flex-col items-center justify-center p-6 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-hover text-ink-muted">
                <Icon name="details" className="h-6 w-6" />
              </div>
              <h3 className="mt-4 text-sm font-extrabold text-ink">
                No Case State Updates Yet
              </h3>
              <p className="mt-1.5 max-w-[260px] text-xs leading-relaxed text-ink-secondary">
                When CyberCase analyzes security events and transitions the case
                graph, delta operations, gaps, and MITRE candidates will appear here.
              </p>
            </div>
          ) : activeTab === "delta" ? (
            /* TAB 1: State Delta Page */
            <div className="space-y-5">
              {/* Version Banner */}
              <div className="rounded-xl border border-[#CAD8CE] bg-[#F1F5F1] p-4">
                <p className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-[#516257]">
                  {isUpdated ? "Case updated" : "Case State unchanged"}
                </p>
                <p className="mt-1 text-sm font-extrabold text-ink">
                  {isUpdated
                    ? `Case State V${currentItem.update.parentVersion} → V${currentItem.update.childVersion}`
                    : `Case State V${currentItem.update.parentVersion} · No new version`}
                </p>
              </div>

              {/* Added Section */}
              <section aria-label="Added operations" className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-extrabold uppercase tracking-wide text-ink">
                    Added ({currentItem.update.added.length})
                  </h3>
                </div>
                {currentItem.update.added.length > 0 ? (
                  <ul className="space-y-2">
                    {currentItem.update.added.map((item) => (
                      <li
                        key={`${item.targetType}:${item.targetId}`}
                        className="rounded-xl border border-line bg-surface p-3 shadow-2xs"
                      >
                        <div className="flex items-center gap-2">
                          <span className="rounded bg-[#E2EAE4] px-1.5 py-0.5 text-[9.5px] font-extrabold uppercase tracking-wide text-[#3E5244]">
                            {readableValue(item.targetType)}
                          </span>
                          <span className="font-mono text-[10px] font-bold text-ink-muted">
                            {item.targetId}
                          </span>
                        </div>
                        <p className="mt-1.5 text-xs leading-relaxed text-ink">
                          {item.summary}
                        </p>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="rounded-xl border border-line bg-surface/50 p-3 text-xs text-ink-muted">
                    No ADD operations in this version.
                  </p>
                )}
              </section>

              {/* Changed Section */}
              <section aria-label="Changed operations" className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-extrabold uppercase tracking-wide text-ink">
                    Changed ({currentItem.update.changed.length})
                  </h3>
                </div>
                {currentItem.update.changed.length > 0 ? (
                  <ul className="space-y-2">
                    {currentItem.update.changed.map((item) => (
                      <li
                        key={`${item.targetType}:${item.targetId}:${item.field}`}
                        className="rounded-xl border border-line bg-surface p-3 shadow-2xs"
                      >
                        <p className="text-xs font-bold text-ink">
                          {item.targetId} · {readableValue(item.field)}
                        </p>
                        <div className="mt-1.5 flex items-center gap-1.5 text-xs text-ink-secondary">
                          <span className="rounded bg-surface-hover px-1.5 py-0.5 font-mono text-[11px]">
                            {formatCaseUpdateValue(item.oldValue)}
                          </span>
                          <span>→</span>
                          <span className="rounded bg-[#E2EAE4] px-1.5 py-0.5 font-mono text-[11px] font-bold text-[#3E5244]">
                            {formatCaseUpdateValue(item.newValue)}
                          </span>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="rounded-xl border border-line bg-surface/50 p-3 text-xs text-ink-muted">
                    No MODIFY operations in this version.
                  </p>
                )}
              </section>

              <p className="text-[10.5px] leading-relaxed text-ink-muted">
                Derived deterministically from the committed Case State delta.
              </p>
            </div>
          ) : activeTab === "unresolved" ? (
            /* TAB 2: Dedicated Current Unresolved Page */
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-extrabold uppercase tracking-wide text-ink">
                  Current Unresolved Information
                </h3>
                <p className="mt-0.5 text-[11px] text-ink-secondary">
                  Active gaps identified in the investigation requiring analyst
                  follow-up or evidence.
                </p>
              </div>

              {unresolvedGaps === null ? (
                <div className="rounded-xl border border-line bg-surface p-4 text-center">
                  <p className="text-xs text-ink-secondary">
                    No validated Gap Analysis is available.
                  </p>
                </div>
              ) : unresolvedGaps.length === 0 ? (
                <div className="rounded-xl border border-[#CAD8CE] bg-[#F1F5F1] p-4 text-center">
                  <p className="text-xs font-bold text-[#3E5244]">
                    All information gaps are resolved for this version.
                  </p>
                </div>
              ) : (
                <ul className="space-y-3">
                  {unresolvedGaps.map((gap, index) => (
                    <li key={`${gap.topic}:${gap.status}:${index}`}>
                      <details className="group overflow-hidden rounded-xl border border-line bg-surface shadow-2xs transition-all">
                        <summary className="flex cursor-pointer list-none select-none items-start justify-between gap-3 p-4 transition-colors hover:bg-surface-hover/60 marker:hidden">
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2">
                              <h4 className="text-xs font-extrabold text-ink transition-colors group-hover:text-primary">
                                {gap.topic}
                              </h4>
                            </div>
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
                                <dt className="font-extrabold text-ink">
                                  Why it matters
                                </dt>
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
                                <dt className="font-extrabold text-ink">
                                  Gap Impact
                                </dt>
                                <dd className="mt-0.5 text-ink-secondary">
                                  This missing information impacts the certainty of threat technique mapping and incident attribution.
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
          ) : (
            /* TAB 3: Dedicated MITRE Candidates Page */
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-extrabold uppercase tracking-wide text-ink">
                  MITRE ATT&amp;CK Candidates
                </h3>
                <p className="mt-0.5 text-[11px] text-ink-secondary">
                  External technique candidates mapped from threat activity claims for this round.
                </p>
              </div>

              {!mitreCandidates || mitreCandidates.length === 0 ? (
                <div className="rounded-xl border border-line bg-surface p-6 text-center space-y-2">
                  <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-surface-hover text-ink-muted">
                    <Icon name="report" className="h-5 w-5" />
                  </div>
                  <h4 className="text-xs font-extrabold text-ink">
                    No MITRE Candidates for this Round
                  </h4>
                  <p className="text-xs leading-relaxed text-ink-secondary max-w-[260px] mx-auto">
                    Technique candidates appear when technical analysis is completed and threat activity maps to ATT&amp;CK patterns.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {mitreCandidates.map((candidate) => (
                    <article
                      key={candidate.associationId}
                      aria-label={`${candidate.techniqueId} MITRE candidate`}
                      className="rounded-xl border border-[#D8D3E3] bg-surface p-4 shadow-2xs space-y-3"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span className="rounded bg-[#EDE9F2] px-1.5 py-0.5 text-[9.5px] font-extrabold uppercase tracking-wide text-[#51495D]">
                            MITRE Candidate
                          </span>
                          <h4 className="mt-1.5 text-xs font-extrabold text-ink">
                            {candidate.techniqueId} — {candidate.techniqueName}
                          </h4>
                        </div>
                        <span className="font-mono text-[10px] font-bold text-ink-muted">
                          {candidate.associationId}
                        </span>
                      </div>

                      {candidate.claims.length > 0 && (
                        <div className="border-t border-line/60 pt-2.5">
                          <p className="text-[10px] font-bold uppercase tracking-wide text-ink-secondary">
                            Linked Analysis Claims ({candidate.claims.length})
                          </p>
                          <ul className="mt-1.5 space-y-1.5">
                            {candidate.claims.map((claim) => (
                              <li
                                key={claim.claimId}
                                className="rounded-lg bg-surface-hover/60 p-2 text-xs leading-relaxed text-ink-secondary"
                              >
                                <div className="flex items-center gap-1.5 mb-0.5">
                                  <span className="font-mono text-[10px] font-bold text-ink bg-surface px-1 py-0.2 rounded border border-line">
                                    {claim.claimId}
                                  </span>
                                  <span className="text-[9.5px] font-medium text-ink-muted capitalize">
                                    {claim.claimType.replaceAll("_", " ")} · {claim.epistemicStatus}
                                  </span>
                                </div>
                                <p className="text-xs text-ink">{claim.text}</p>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {candidate.reason && (
                        <div className="border-t border-line/60 pt-2.5">
                          <p className="text-[10px] font-bold uppercase tracking-wide text-ink-secondary">
                            Why this candidate?
                          </p>
                          <p className="mt-1 text-xs leading-relaxed text-ink-secondary">
                            {candidate.reason}
                          </p>
                        </div>
                      )}

                      <div className="flex flex-wrap gap-1.5 pt-1 text-[9.5px] font-semibold text-[#665B73]">
                        <span className="rounded-full border border-[#D8D3E3] bg-[#F7F5F9] px-2 py-0.5">
                          Candidate only
                        </span>
                        <span className="rounded-full border border-[#D8D3E3] bg-[#F7F5F9] px-2 py-0.5">
                          External technical context
                        </span>
                        <span className="rounded-full border border-[#D8D3E3] bg-[#F7F5F9] px-2 py-0.5">
                          Not incident evidence
                        </span>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
