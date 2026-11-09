"use client";

import { useParams } from "next/navigation";
import { Icon } from "@/components/icons";
import { Markdown } from "@/components/Markdown";
import { hasThai } from "@/lib/language";
import { SummaryUnits } from "./SummaryUnits";
import { useCaseOverview } from "./useCaseOverview";

export function AnalysisSummary() {
  const { caseId } = useParams<{ caseId: string }>();
  const { analysisResult, overview } = useCaseOverview(caseId);
  if (!analysisResult || !overview.hasAnalysis) return null;

  return (
    <section
      id="section-summary"
      aria-labelledby="overview-summary-heading"
      className="sheet min-w-0 scroll-mt-6"
    >
      <div className="card-head">
        <h2
          id="overview-summary-heading"
          className="flex items-center gap-2.5 text-lg font-semibold text-ink"
        >
          <Icon name="summary" className="text-xl text-primary" />
          What happened
        </h2>
      </div>
      <div className="px-6 py-5 text-sm text-ink [overflow-wrap:anywhere] [&_p]:mb-3 [&_p]:text-sm [&_p]:leading-7">
        {overview.summaryUnits.length > 0 ? (
          <SummaryUnits
            caseId={caseId}
            units={overview.summaryUnits}
            thai={hasThai(overview.incidentSummary)}
          />
        ) : (
          <Markdown content={overview.incidentSummary} />
        )}
      </div>
    </section>
  );
}
