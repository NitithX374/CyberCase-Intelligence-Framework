"use client";

import { useState, type ReactNode } from "react";
import { useParams, useSearchParams } from "next/navigation";
import type { SourceMessageRef } from "@/features/citations/types";
import { SourceDrawer } from "@/features/citations/SourceDrawer";
import { useSourceDrawer } from "@/features/citations/useSourceDrawer";
import { CaseFindingsSection } from "./CaseFindingsSection";
import { useCaseOverview } from "./useCaseOverview";

type FindingsFilter = "all" | "flagged" | "not_confirmed";

function filterFromStatus(status: string | null | undefined): FindingsFilter {
  return status === "flagged" || status === "not_confirmed" ? status : "all";
}

export function AnalysisFindings({ heading }: { heading?: ReactNode }) {
  const { caseId } = useParams<{ caseId: string }>();
  const searchParams = useSearchParams();
  const { analysisResult, overview } = useCaseOverview(caseId);
  const drawer = useSourceDrawer();
  const unconfirmed = overview.findings.filter(
    (finding) => finding.epistemicStatus === "not_confirmed",
  );
  const flagged = overview.findings.filter(
    (finding) => finding.traceability.semanticSupport === "not_supported",
  );
  const [filter, setFilter] = useState<FindingsFilter>(() => {
    const status = searchParams?.get("status");
    if (status || searchParams?.get("finding")) return filterFromStatus(status);
    return flagged.length > 0 ? "flagged" : "all";
  });

  if (!analysisResult || !overview.hasAnalysis) return null;
  const displayedFindings =
    filter === "flagged" ? flagged : filter === "not_confirmed" ? unconfirmed : overview.findings;

  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
    citationRole?: "supporting" | "conflicting",
  ) => drawer.toggle({ sourceRef, anchorElement, key, citationRole });

  return (
    <div className="w-full">
      <div className="card-head">
        {heading}
        {(flagged.length > 0 || unconfirmed.length > 0 || filter !== "all") && (
          <div
            role="group"
            aria-label="Show findings"
            className="inline-flex flex-wrap rounded-[9px] bg-surface-hover p-[3px]"
          >
            <FilterButton pressed={filter === "all"} onClick={() => setFilter("all")}>
              All <Count>{overview.findings.length}</Count>
            </FilterButton>
            <FilterButton pressed={filter === "flagged"} onClick={() => setFilter("flagged")}>
              To check <Count>{flagged.length}</Count>
            </FilterButton>
            <FilterButton
              pressed={filter === "not_confirmed"}
              onClick={() => setFilter("not_confirmed")}
            >
              Not confirmed <Count>{unconfirmed.length}</Count>
            </FilterButton>
          </div>
        )}
      </div>
      {filter === "not_confirmed" && (
        <p className="border-b border-line px-6 py-3 text-sm leading-6 text-ink-secondary">
          These findings are marked as not confirmed in the saved analysis. Review their Source
          linkage and cited text before relying on them; semantic support is shown separately.
        </p>
      )}

      {filter !== "all" && displayedFindings.length === 0 ? (
        <p className="px-6 py-6 text-sm text-ink-muted">
          {filter === "flagged"
            ? "No findings to check in this analysis."
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
      className={`inline-flex min-h-9 items-center gap-1.5 rounded-[7px] px-3.5 text-sm transition-[color,background-color,box-shadow] duration-150 ${
        pressed
          ? "bg-surface font-semibold text-primary shadow-[0_2px_6px_rgba(24,24,28,0.08)]"
          : "text-ink-muted hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}

function Count({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-lg bg-primary-soft px-1.5 text-xs font-medium text-primary">
      {children}
    </span>
  );
}
