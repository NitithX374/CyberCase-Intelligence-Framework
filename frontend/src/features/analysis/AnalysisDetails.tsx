"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import type { SourceMessageRef } from "@/features/citations/types";
import { SourceDrawer } from "@/features/citations/SourceDrawer";
import { useSourceDrawer } from "@/features/citations/useSourceDrawer";
import { CaseDetails } from "./CaseDetails";
import { TechnicalContextView } from "./technical-context/TechnicalContextView";
import { useCaseOverview } from "./useCaseOverview";

export function AnalysisDetails() {
  const { caseId } = useParams<{ caseId: string }>();
  const { analysisResult, sources, overview } = useCaseOverview(caseId);
  const drawer = useSourceDrawer();
  if (!analysisResult || !overview.hasAnalysis) return null;
  const hasSavedDetails =
    overview.parties.length + overview.timeline.length + overview.impacts.length > 0;

  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
    citationRole?: "supporting" | "conflicting",
  ) => drawer.toggle({ sourceRef, anchorElement, key, citationRole });

  return (
    <>
      <div className="mx-auto w-full max-w-[52rem] px-5 pt-8 sm:px-8">
        {hasSavedDetails ? (
          <CaseDetails
            caseId={caseId}
            timeline={overview.timeline}
            parties={overview.parties}
            impacts={overview.impacts}
            onSelectSource={handleSelectSource}
            activeSourceKey={drawer.openKey}
          />
        ) : (
          <section aria-label="Case details" className="text-sm leading-7 text-ink-secondary">
            <p>
              {overview.findings.length > 0
                ? "People, dates, events and impacts are recorded in the claims."
                : "No claims were recorded in this analysis."}
            </p>
            <Link
              href={analysisPath(caseId, "findings")}
              className="font-medium text-ink underline underline-offset-4"
            >
              Open Findings and their sources
            </Link>
          </section>
        )}
      </div>
      <TechnicalContextView analysisResult={analysisResult} sources={sources} />
      {drawer.open && (
        <SourceDrawer
          sourceRef={drawer.open.sourceRef}
          anchorElement={drawer.open.anchorElement}
          onClose={drawer.close}
          citationRole={drawer.open.citationRole}
        />
      )}
    </>
  );
}
