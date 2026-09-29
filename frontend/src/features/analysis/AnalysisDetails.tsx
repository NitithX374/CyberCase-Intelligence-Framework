"use client";

import { useParams } from "next/navigation";
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

  const handleSelectSource = (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    key: string,
    citationRole?: "supporting" | "conflicting",
  ) => drawer.toggle({ sourceRef, anchorElement, key, citationRole });

  return (
    <>
      <div className="mx-auto w-full max-w-[52rem] px-5 pt-8 sm:px-8">
        <CaseDetails
          timeline={overview.timeline}
          parties={overview.parties}
          impacts={overview.impacts}
          onSelectSource={handleSelectSource}
          activeSourceKey={drawer.openKey}
        />
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
