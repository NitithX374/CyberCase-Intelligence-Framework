"use client";

import { useParams } from "next/navigation";
import { Icon } from "@/components/icons";
import { LegalReferenceView } from "@/features/legal/LegalReferenceView";
import { readLegalReference } from "@/features/legal/legalReference";
import { TechnicalContextView } from "./technical-context/TechnicalContextView";
import { buildTechnicalContext } from "./technical-context/technicalContext";
import { useCaseOverview } from "./useCaseOverview";

const PAGES = {
  technical: {
    title: "ATT&CK techniques",
    icon: "technical",
    color: "text-technical-ink",
    note: "ATT&CK techniques an outside lookup matched to sentences of this case. A pointer, not a case fact.",
  },
  legal: {
    title: "Related laws",
    icon: "legal",
    color: "text-legal-ink",
    note: "Thai legal provisions an outside service matched to this case. A starting point for legal review, not legal advice.",
  },
} as const;

export function OutsideSourcePage({ kind }: { kind: "technical" | "legal" }) {
  const { caseId } = useParams<{ caseId: string }>();
  const { analysisResult, sources, overview } = useCaseOverview(caseId);
  if (!analysisResult || !overview.hasAnalysis) return null;

  const page = PAGES[kind];
  const count =
    kind === "technical"
      ? buildTechnicalContext(analysisResult, sources).techniques.length
      : (readLegalReference(analysisResult)?.provisions.length ?? 0);

  return (
    <section aria-labelledby={`${kind}-heading`} className="sheet min-w-0">
      <div className="card-head">
        <h1
          id={`${kind}-heading`}
          className="flex flex-1 items-center gap-2.5 text-lg font-semibold text-ink"
        >
          <Icon name={page.icon} className={`text-xl ${page.color}`} />
          {page.title}
          {count > 0 && <span className="count-pill">{count}</span>}
        </h1>
        <p className="basis-full text-sm text-ink-muted">{page.note}</p>
      </div>
      <div className="px-6 pb-6">
        {kind === "technical" ? (
          <TechnicalContextView analysisResult={analysisResult} sources={sources} />
        ) : (
          <LegalReferenceView analysisResult={analysisResult} />
        )}
      </div>
    </section>
  );
}
