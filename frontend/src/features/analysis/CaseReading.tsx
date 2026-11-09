"use client";

import { useParams } from "next/navigation";
import { Icon } from "@/components/icons";
import { LegalReferenceView } from "@/features/legal/LegalReferenceView";
import { AnalysisFindings } from "./AnalysisFindings";
import { TechnicalContextView } from "./technical-context/TechnicalContextView";
import { useCaseOverview } from "./useCaseOverview";

export function CaseReading() {
  const { caseId } = useParams<{ caseId: string }>();
  const { analysisResult, sources, overview } = useCaseOverview(caseId);
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

      <details id="section-references" className="group sheet scroll-mt-6">
        <summary className="card-head cursor-pointer list-none border-b-0 group-open:border-b">
          <h2 className="flex flex-1 items-center gap-2.5 text-lg font-semibold text-ink">
            <Icon name="references" className="text-xl text-primary" />
            Outside references
          </h2>
          <span className="flex items-center gap-2 text-sm text-ink-muted">
            ATT&CK and Thai law. Not case facts.
            <Icon name="chevron" className="text-xl transition-transform group-open:rotate-180" />
          </span>
        </summary>
        <div className="px-6 pb-6">
          <p className="pt-4 text-sm text-ink-secondary">
            These come from outside services, matched to the case text. Use them as pointers, not as
            findings.
          </p>
          <TechnicalContextView analysisResult={analysisResult} sources={sources} />
          <LegalReferenceView analysisResult={analysisResult} />
        </div>
      </details>
    </div>
  );
}
