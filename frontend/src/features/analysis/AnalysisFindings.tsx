"use client";

import { useState, type ReactNode } from "react";
import { useParams, useSearchParams } from "next/navigation";
import type { SourceMessageRef } from "@/features/citations/types";
import { SourceDrawer } from "@/features/citations/SourceDrawer";
import { useSourceDrawer } from "@/features/citations/useSourceDrawer";
import { CaseFindingsSection } from "./CaseFindingsSection";
import { useCaseOverview } from "./useCaseOverview";

export function AnalysisFindings() {
  const { caseId } = useParams<{ caseId: string }>();
  const searchParams = useSearchParams();
  const { analysisResult, overview } = useCaseOverview(caseId);
  const drawer = useSourceDrawer();
  const [onlyUnconfirmed, setOnlyUnconfirmed] = useState(
    () => searchParams?.get("status") === "not_confirmed",
  );
  const [searchQuery, setSearchQuery] = useState("");

  if (!analysisResult || !overview.hasAnalysis) return null;

  const unconfirmed = overview.findings.filter(
    (finding) => finding.epistemicStatus === "not_confirmed",
  );
  const filtered = onlyUnconfirmed && unconfirmed.length > 0;
  const baseFindings = filtered ? unconfirmed : overview.findings;
  const query = searchQuery.trim().toLowerCase();
  const displayedFindings = query
    ? baseFindings.filter(
        (finding) =>
          finding.text.toLowerCase().includes(query) ||
          finding.id.toLowerCase().includes(query) ||
          (finding.reasoningSummary && finding.reasoningSummary.toLowerCase().includes(query)),
      )
    : baseFindings;

  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
    citationRole?: "supporting" | "conflicting",
  ) => drawer.toggle({ sourceRef, anchorElement, key, citationRole });

  return (
    <div className="mx-auto w-full max-w-[52rem] px-5 sm:px-8">
      <div className="pt-6 space-y-4">
        {overview.findings.length > 3 && (
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search findings (e.g. name, date, case number)…"
              className="w-full rounded-xl border border-line bg-surface px-4 py-2.5 text-sm text-ink placeholder:text-ink-muted transition-colors focus:border-line-strong focus:outline-none focus:ring-1 focus:ring-ink/10"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-ink-muted hover:text-ink px-1.5 py-0.5 rounded"
              >
                Clear
              </button>
            )}
          </div>
        )}

        {unconfirmed.length > 0 && (
          <div>
            <div role="group" aria-label="Show findings" className="flex items-center gap-5">
              <FilterButton pressed={!filtered} onClick={() => setOnlyUnconfirmed(false)}>
                All <span className="text-ink-muted">{overview.findings.length}</span>
              </FilterButton>
              <FilterButton pressed={filtered} onClick={() => setOnlyUnconfirmed(true)}>
                Not confirmed <span className="text-unresolved">{unconfirmed.length}</span>
              </FilterButton>
            </div>
            {filtered && (
              <p className="mt-3 max-w-[68ch] text-[13px] leading-6 text-ink-secondary">
                These findings are marked as not confirmed in the saved analysis. Review their
                Source linkage and cited text before relying on them; semantic support is shown
                separately.
              </p>
            )}
          </div>
        )}

        {query && (
          <div className="flex items-center justify-between text-xs text-ink-muted">
            <span>
              Found {displayedFindings.length} of {baseFindings.length} findings
            </span>
          </div>
        )}
      </div>

      {displayedFindings.length === 0 && query ? (
        <div className="py-12 text-center text-sm text-ink-muted">
          No findings matching &ldquo;{searchQuery}&rdquo;.
          <div className="mt-2">
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="text-xs font-medium text-ink underline underline-offset-2"
            >
              Clear search filter
            </button>
          </div>
        </div>
      ) : (
        <CaseFindingsSection
          key={`${analysisResult.id}:${filtered ? "not_confirmed" : "all"}:${query}`}
          caseId={caseId}
          findings={displayedFindings}
          focusId={searchParams?.get("finding") ?? null}
          onSelectSource={handleSelectSource}
          activeSourceKey={drawer.openKey}
        />
      )}
      {drawer.open && (
        <SourceDrawer
          sourceRef={drawer.open.sourceRef}
          anchorElement={drawer.open.anchorElement}
          onClose={drawer.close}
          citationRole={drawer.open.citationRole}
        />
      )}
    </div>
  );
}

function FilterButton({
  pressed,
  onClick,
  children,
}: {
  pressed: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={onClick}
      className={`text-[13px] transition-colors ${
        pressed ? "font-semibold text-ink" : "font-medium text-ink-muted hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}
