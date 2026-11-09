"use client";

import { useParams } from "next/navigation";
import { Icon, type IconName } from "@/components/icons";
import { AnalysisDetails } from "./AnalysisDetails";
import { useCaseOverview } from "./useCaseOverview";

const PAGES: Record<
  "timeline" | "people" | "impact",
  { title: string; icon: IconName; note: string; empty: string }
> = {
  timeline: {
    title: "Timeline",
    icon: "timeline",
    note: "Events in the order the sources give them. Each one links to the findings it comes from.",
    empty: "No events were drawn from the findings of this analysis.",
  },
  people: {
    title: "People",
    icon: "people",
    note: "Who appears in the findings. Each line is a finding that mentions them, numbered as in Findings; open it for the full text and its source.",
    empty: "No people or organisations were drawn from the findings of this analysis.",
  },
  impact: {
    title: "Impact",
    icon: "impact",
    note: "Losses and effects the sources report.",
    empty: "No impact was drawn from the findings of this analysis.",
  },
};

export function CaseFacts({ kind }: { kind: "timeline" | "people" | "impact" }) {
  const { caseId } = useParams<{ caseId: string }>();
  const { overview } = useCaseOverview(caseId);
  if (!overview.hasAnalysis) return null;

  const page = PAGES[kind];
  const count =
    kind === "timeline"
      ? overview.timeline.length
      : kind === "people"
        ? overview.parties.length
        : overview.impacts.length;

  return (
    <section aria-labelledby={`${kind}-heading`} className="sheet min-w-0">
      <div className="card-head">
        <h1
          id={`${kind}-heading`}
          className="flex flex-1 items-center gap-2.5 text-lg font-semibold text-ink"
        >
          <Icon name={page.icon} className="text-xl text-primary" />
          {page.title}
          <span className="count-pill">{count}</span>
        </h1>
        <p className="basis-full text-sm text-ink-muted">{page.note}</p>
      </div>
      <div className="px-6 pb-6">
        {count === 0 ? (
          <p className="pt-6 text-base text-ink-secondary">{page.empty}</p>
        ) : (
          <AnalysisDetails withTechnical={false} only={kind} />
        )}
      </div>
    </section>
  );
}
