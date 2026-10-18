"use client";

import type { SourceMessageRef } from "@/features/citations/types";
import type { CaseImpact, CaseParty, CaseTimelineEvent, ClaimBacked } from "./types";
import { DetailSection } from "./DetailSection";
import { FoldedList } from "./FoldedList";
import { Backing } from "./Backing";

export interface CaseDetailsProps {
  caseId?: string;
  timeline: CaseTimelineEvent[];
  parties: CaseParty[];
  impacts: CaseImpact[];
  onSelectSource: (
    sourceRef: SourceMessageRef,
    anchorElement: HTMLElement,
    sourceKey: string,
  ) => void;
  activeSourceKey: string | null;
}

export function CaseDetails({
  caseId,
  timeline,
  parties,
  impacts,
  onSelectSource,
  activeSourceKey,
}: CaseDetailsProps) {
  if (!timeline.length && !parties.length && !impacts.length) return null;
  const backing = (row: ClaimBacked, owner: string) => (
    <Backing
      row={row}
      caseId={caseId}
      owner={owner}
      onSelectSource={onSelectSource}
      activeSourceKey={activeSourceKey}
    />
  );

  return (
    <div className="space-y-10">
      {timeline.length > 0 && (
        <DetailSection id="case-timeline" title="Timeline" count={timeline.length}>
          <FoldedList
            items={timeline}
            label="events"
            as="ol"
            className="divide-y divide-line border-y border-line"
            render={(item, index) => (
              <li
                key={index}
                className="grid gap-x-4 gap-y-0.5 py-3 sm:grid-cols-[9rem_minmax(0,1fr)]"
              >
                <p className="text-[13px] leading-7 text-ink-secondary">
                  {item.time ?? "No date or time extracted; check the linked claim"}
                </p>
                <div className="min-w-0">
                  <p className="text-[15px] leading-7 text-ink">{item.event}</p>
                  {backing(item, `timeline-${index}`)}
                </div>
              </li>
            )}
          />
        </DetailSection>
      )}

      {parties.length > 0 && (
        <DetailSection id="case-parties" title="Parties" count={parties.length}>
          <FoldedList
            items={parties}
            label="parties"
            className="divide-y divide-line border-y border-line"
            render={(party, index) => (
              <li
                key={index}
                className="grid gap-x-4 gap-y-0.5 py-3 sm:grid-cols-[minmax(0,14rem)_minmax(0,1fr)]"
              >
                <p className="text-[15px] font-semibold leading-7 text-ink">{party.name}</p>
                <div className="min-w-0">
                  <p className="text-[15px] leading-7 text-ink-secondary">
                    {party.role === null ? "No role extracted; check the linked claim" : party.role}
                  </p>
                  {backing(party, `party-${index}`)}
                </div>
              </li>
            )}
          />
        </DetailSection>
      )}

      {impacts.length > 0 && (
        <DetailSection id="case-impacts" title="Impact" count={impacts.length}>
          <FoldedList
            items={impacts}
            label="impacts"
            className="divide-y divide-line border-y border-line"
            render={(impact, index) => (
              <li key={index} className="py-3">
                <p className="text-[15px] leading-7 text-ink">{impact.description}</p>
                {backing(impact, `impact-${index}`)}
              </li>
            )}
          />
        </DetailSection>
      )}
    </div>
  );
}
