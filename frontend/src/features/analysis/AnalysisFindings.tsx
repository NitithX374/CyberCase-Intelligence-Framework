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
  if (!analysisResult || !overview.hasAnalysis) return null;

  const unconfirmed = overview.findings.filter(
    (finding) => finding.epistemicStatus === "not_confirmed",
  );
  const filtered = onlyUnconfirmed && unconfirmed.length > 0;
  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
    citationRole?: "supporting" | "conflicting",
  ) => drawer.toggle({ sourceRef, anchorElement, key, citationRole });

  return (
    <div className="mx-auto w-full max-w-[52rem] px-5 sm:px-8">
      {unconfirmed.length > 0 && (
        <div className="pt-6">
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
              Each of these names a source, but its quotation was not found there word for word.
              Check it against the source before you rely on it.
            </p>
          )}
        </div>
      )}
      <CaseFindingsSection
        key={`${analysisResult.id}:${filtered ? "not_confirmed" : "all"}`}
        caseId={caseId}
        findings={filtered ? unconfirmed : overview.findings}
        focusId={searchParams?.get("finding") ?? null}
        onSelectSource={handleSelectSource}
        activeSourceKey={drawer.openKey}
      />
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
