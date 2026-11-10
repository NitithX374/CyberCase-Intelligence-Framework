"use client";

import { useParams } from "next/navigation";
import { Icon } from "@/components/icons";
import { AnalysisFindings } from "./AnalysisFindings";
import { useCaseOverview } from "./useCaseOverview";

export function CaseReading() {
  const { caseId } = useParams<{ caseId: string }>();
  const { analysisResult, overview } = useCaseOverview(caseId);
  if (!analysisResult || !overview.hasAnalysis) return null;

  return (
    <div className="flex min-w-0 flex-col gap-5">
      <section
        id="section-findings"
        aria-labelledby="findings-heading"
        className="sheet @container min-w-0 scroll-mt-6 overflow-hidden"
      >
        <AnalysisFindings
          heading={
            <h2
              id="findings-heading"
              className="flex flex-1 items-center gap-2.5 text-lg font-semibold text-ink"
            >
              <Icon name="findings" className="text-xl text-primary" />
              Findings
            </h2>
          }
        />
      </section>
    </div>
  );
}
