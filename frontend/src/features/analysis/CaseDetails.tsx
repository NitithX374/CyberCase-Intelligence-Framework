"use client";

import { useState, type ReactNode } from "react";
import type { SourceMessageRef } from "@/features/sources/types";
import { SourceCitationChip } from "@/features/sources/SourceCitationChip";
import type { CaseImpact, CaseParty, CaseTimelineEvent } from "./types";

/** Past this many rows a list shows the first ones and offers the rest. */
const VISIBLE_ROWS = 6;

interface CaseDetailsProps {
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

/**
 * What happened when, who was involved, and what it cost, as the analysis
 * wrote them. Each row carries the sources of the claims it cites, so it can
 * be checked the way a finding can.
 */
export function CaseDetails({
  timeline,
  parties,
  impacts,
  onSelectSource,
  activeSourceKey,
}: CaseDetailsProps) {
  if (!timeline.length && !parties.length && !impacts.length) return null;
  const hasSide = parties.length > 0 || impacts.length > 0;
  const backing = (row: { sources: SourceMessageRef[]; inferred: boolean }, owner: string) => (
    <Backing
      row={row}
      owner={owner}
      onSelectSource={onSelectSource}
      activeSourceKey={activeSourceKey}
    />
  );

  return (
    <div
      className={`mt-12 grid gap-10 ${
        timeline.length > 0 && hasSide ? "md:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]" : ""
      }`}
    >
      {timeline.length > 0 && (
        <DetailSection id="case-timeline" title="Timeline" count={timeline.length}>
          <FoldedList
            items={timeline}
            label="events"
            as="ol"
            className="border-l border-line-strong"
            render={(item, index) => (
              <li key={index} className="relative pb-5 pl-5 last:pb-0">
                <span
                  aria-hidden="true"
                  className="absolute top-[5px] -left-[5.5px] h-2.5 w-2.5 rounded-full border-2 border-surface bg-ink-secondary"
                />
                <p className="text-[13px] font-medium text-ink-secondary">{item.time}</p>
                <p className="mt-0.5 text-[15px] leading-7 text-ink">{item.event}</p>
                {backing(item, `timeline-${index}`)}
              </li>
            )}
          />
        </DetailSection>
      )}

      {hasSide && (
        <div className="space-y-10">
          {parties.length > 0 && (
            <DetailSection id="case-parties" title="Parties" count={parties.length}>
              <FoldedList
                items={parties}
                label="parties"
                className="divide-y divide-line"
                render={(party, index) => (
                  <li key={index} className="py-3 first:pt-0">
                    <p className="text-[15px] font-semibold text-ink">{party.name}</p>
                    <p className="mt-0.5 text-[13px] leading-6 text-ink-secondary">{party.role}</p>
                    {backing(party, `party-${index}`)}
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
                className="space-y-3"
                render={(impact, index) => (
                  <li key={index} className="flex gap-3">
                    <span
                      aria-hidden="true"
                      className="mt-[11px] h-1.5 w-1.5 shrink-0 rounded-full bg-unresolved"
                    />
                    <div className="min-w-0">
                      <p className="text-[15px] leading-7 text-ink">{impact.description}</p>
                      {backing(impact, `impact-${index}`)}
                    </div>
                  </li>
                )}
              />
            </DetailSection>
          )}
        </div>
      )}
    </div>
  );
}

function DetailSection({
  id,
  title,
  count,
  children,
}: {
  id: string;
  title: string;
  count: number;
  children: ReactNode;
}) {
  return (
    <section aria-labelledby={`${id}-heading`} className="min-w-0">
      <h2
        id={`${id}-heading`}
        className="flex items-baseline gap-2 text-base font-semibold text-ink"
      >
        {title} <span className="text-[13px] font-medium text-ink-muted">{count}</span>
      </h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function FoldedList<T>({
  items,
  label,
  as: List = "ul",
  className,
  render,
}: {
  items: T[];
  label: string;
  as?: "ul" | "ol";
  className: string;
  render: (item: T, index: number) => ReactNode;
}) {
  const [expanded, setExpanded] = useState(false);
  const folds = items.length > VISIBLE_ROWS;
  const shown = expanded || !folds ? items : items.slice(0, VISIBLE_ROWS);

  return (
    <>
      <List className={className}>{shown.map(render)}</List>
      {folds && (
        <button
          type="button"
          onClick={() => setExpanded((open) => !open)}
          className="mt-3 text-[13px] font-medium text-ink-secondary hover:text-ink"
        >
          {expanded ? "Show fewer" : `Show all ${items.length}`}{" "}
          <span className="sr-only">{label}</span>
        </button>
      )}
    </>
  );
}

/** The row's sources as chips, after an Inference tag when nothing it cites is reported. */
function Backing({
  row,
  owner,
  onSelectSource,
  activeSourceKey,
}: {
  row: { sources: SourceMessageRef[]; inferred: boolean };
  owner: string;
  onSelectSource: CaseDetailsProps["onSelectSource"];
  activeSourceKey: string | null;
}) {
  if (!row.inferred && !row.sources.length) return null;
  return (
    <div className="mt-2 flex flex-wrap items-center gap-1.5">
      {row.inferred && (
        <span className="tag border border-line-strong text-ink-secondary">Inference</span>
      )}
      {row.sources.map((source, index) => {
        const key = `${owner}-${source.id}-${index}`;
        return (
          <SourceCitationChip
            key={key}
            sourceRef={source}
            sourceKey={key}
            isActive={activeSourceKey === key}
            onSelect={onSelectSource}
          />
        );
      })}
    </div>
  );
}
