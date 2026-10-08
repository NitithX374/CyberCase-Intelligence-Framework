"use client";

import { useState, type ReactNode } from "react";
import { useParams, useSearchParams } from "next/navigation";
import type { SourceMessageRef } from "@/features/citations/types";
import { SourceDrawer } from "@/features/citations/SourceDrawer";
import { useSourceDrawer } from "@/features/citations/useSourceDrawer";
import { CaseFindingsSection } from "./CaseFindingsSection";
import { useCaseOverview } from "./useCaseOverview";

type FindingsFilter = "all" | "supported" | "not_confirmed";

export function AnalysisFindings() {
  const { caseId } = useParams<{ caseId: string }>();
  const searchParams = useSearchParams();
  const { analysisResult, overview } = useCaseOverview(caseId);
  const drawer = useSourceDrawer();
  const [filter, setFilter] = useState<FindingsFilter>(() =>
    searchParams?.get("status") === "not_confirmed" ? "not_confirmed" : "all",
  );

  if (!analysisResult || !overview.hasAnalysis) return null;

  const unconfirmed = overview.findings.filter(
    (finding) => finding.epistemicStatus === "not_confirmed",
  );
  const supported = overview.findings.filter(
    (finding) => finding.traceability.semanticSupport === "supported",
  );
  const displayedFindings =
    filter === "supported"
      ? supported
      : filter === "not_confirmed"
        ? unconfirmed
        : overview.findings;

  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
    citationRole?: "supporting" | "conflicting",
  ) => drawer.toggle({ sourceRef, anchorElement, key, citationRole });

  return (
    <div className="mx-auto w-full max-w-[52rem] px-5 sm:px-8">
      <div className="pt-6 space-y-4">
        {(supported.length > 0 || unconfirmed.length > 0 || filter !== "all") && (
          <div>
            <div
              role="group"
              aria-label="Show findings"
              className="flex flex-wrap items-center gap-x-5 gap-y-3"
            >
              <FilterButton pressed={filter === "all"} onClick={() => setFilter("all")}>
                All <span className="text-ink-muted">{overview.findings.length}</span>
              </FilterButton>
              <FilterButton pressed={filter === "supported"} onClick={() => setFilter("supported")}>
                Supported <span className="text-established">{supported.length}</span>
              </FilterButton>
              <FilterButton
                pressed={filter === "not_confirmed"}
                onClick={() => setFilter("not_confirmed")}
              >
                Not confirmed <span className="text-unresolved">{unconfirmed.length}</span>
              </FilterButton>
            </div>
            {filter === "not_confirmed" && (
              <p className="mt-3 max-w-[68ch] text-[13px] leading-6 text-ink-secondary">
                These findings are marked as not confirmed in the saved analysis. Review their
                Source linkage and cited text before relying on them; semantic support is shown
                separately.
              </p>
            )}
          </div>
        )}
      </div>

      {filter !== "all" && displayedFindings.length === 0 ? (
        <p className="py-6 text-sm text-ink-muted">
          {filter === "supported"
            ? "No supported findings in this analysis."
            : "No findings marked not confirmed."}
        </p>
      ) : (
        <CaseFindingsSection
          key={`${analysisResult.id}:${filter}`}
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
