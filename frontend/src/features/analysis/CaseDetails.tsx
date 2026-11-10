"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { analysisPath } from "@/lib/casePaths";
import type { SourceMessageRef } from "@/features/citations/types";
import { SourceCitationChip } from "@/features/citations/SourceCitationChip";
import { UNCONFIRMED_NOTES } from "@/features/citations/unconfirmed";
import type { CaseImpact, CaseParty, CaseTimelineEvent, ClaimBacked } from "./types";

export function ClaimViewReview({ row, caseId }: { row: ClaimBacked; caseId?: string }) {
  return (
    <details className="mt-2 text-xs leading-6 text-ink-secondary">
      <summary className="cursor-pointer font-medium">Related findings</summary>
      <ul className="mt-2 space-y-2 border-l border-line pl-3" aria-label="Related findings">
        {(row.linkedClaims ?? []).map((claim) => (
          <li key={claim.id}>
            {caseId ? (
              <Link
                href={`${analysisPath(caseId, "findings")}?finding=${encodeURIComponent(claim.id)}`}
                className="font-medium underline underline-offset-2"
              >
                View finding
              </Link>
            ) : (
              <span className="font-medium">Finding</span>
            )}
            : {claim.text}
          </li>
        ))}
      </ul>
    </details>
  );
}

const VISIBLE_ROWS = 6;

const AMOUNT =
  /(?:(?:฿|\$|THB|USD)\s?[\d๐-๙][\d๐-๙,.]*)|(?:[\d๐-๙][\d๐-๙,.]*\s?(?:ล้าน\s?)?(?:baht|บาท|THB|USD|dollars?))/i;

function amountIn(text: string): string | null {
  return text.match(AMOUNT)?.[0].trim() ?? null;
}

function isClockTime(time: string | null): boolean {
  return Boolean(
    time &&
    (/\d{4}|[๐-๙]{4}/.test(time) ||
      /\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b/i.test(time) ||
      /(มกรา|กุมภา|มีนา|เมษา|พฤษภา|มิถุนา|กรกฎา|สิงหา|กันยา|ตุลา|พฤศจิกา|ธันวา)/.test(time)),
  );
}

function FindingRef({ caseId, id, number }: { caseId: string; id: string; number?: number }) {
  return (
    <Link
      href={findingHref(caseId, id)}
      className="inline-flex min-h-6 items-center rounded-md px-1.5 text-xs font-semibold text-ink underline underline-offset-3 hover:bg-surface-hover"
    >
      {number ? `Finding ${number}` : "View finding"}
    </Link>
  );
}

function findingHref(caseId: string, id: string): string {
  return `${analysisPath(caseId, "findings")}?finding=${encodeURIComponent(id)}`;
}

interface CaseDetailsProps {
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
  only?: "timeline" | "people" | "impact";
  findingNumbers?: Record<string, number>;
}

export function CaseDetails({
  caseId,
  timeline: allTimeline,
  parties: allParties,
  impacts: allImpacts,
  onSelectSource,
  activeSourceKey,
  only,
  findingNumbers,
}: CaseDetailsProps) {
  const timeline = !only || only === "timeline" ? allTimeline : [];
  const parties = !only || only === "people" ? allParties : [];
  const impacts = !only || only === "impact" ? allImpacts : [];
  const limit = only ? Infinity : VISIBLE_ROWS;
  if (!timeline.length && !parties.length && !impacts.length) return null;
  const hasSide = parties.length > 0 || impacts.length > 0;
  const backing = (row: ClaimBacked, owner: string, showClaims = true) => (
    <Backing
      row={row}
      caseId={caseId}
      owner={owner}
      onSelectSource={onSelectSource}
      activeSourceKey={activeSourceKey}
      findingNumbers={findingNumbers}
      showClaims={showClaims}
    />
  );
  const impactsShown = [...impacts].sort(
    (first, second) =>
      Number(Boolean(amountIn(second.description))) - Number(Boolean(amountIn(first.description))),
  );

  return (
    <div
      className={`grid grid-cols-[minmax(0,1fr)] gap-10 ${
        timeline.length > 0 && hasSide ? "md:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]" : ""
      }`}
    >
      {timeline.length > 0 && (
        <DetailSection
          hideTitle={Boolean(only)}
          id="case-timeline"
          title="Timeline"
          count={timeline.length}
        >
          <FoldedList
            limit={limit}
            items={timeline}
            label="events"
            as="ol"
            className=""
            render={(item, index) => {
              const clock = isClockTime(item.time);
              const next = timeline[index + 1];
              return (
                <li
                  key={index}
                  className="grid grid-cols-[6.5rem_1.25rem_minmax(0,1fr)] gap-x-3 sm:grid-cols-[9rem_1.5rem_minmax(0,1fr)]"
                >
                  <p
                    className={`pt-0.5 text-right font-mono text-xs leading-5 [overflow-wrap:anywhere] ${clock ? "font-bold text-ink" : "text-ink-secondary"}`}
                  >
                    {item.time ?? "No date or time given; see the linked finding"}
                  </p>
                  <div aria-hidden="true" className="flex flex-col items-center">
                    <span
                      className={
                        clock
                          ? "mt-1 h-3.5 w-3.5 shrink-0 rounded-full bg-ink"
                          : "mt-1 h-3 w-3 shrink-0 rounded-full border-2 border-ink"
                      }
                    />
                    {next && (
                      <span
                        className={`mt-1 w-0 flex-1 border-l-2 border-line-strong ${isClockTime(next.time) ? "" : "border-dashed"}`}
                      />
                    )}
                  </div>
                  <div className="min-w-0 pb-8">
                    <p className="text-base text-ink">{item.event}</p>
                    {backing(item, `timeline-${index}`)}
                  </div>
                </li>
              );
            }}
          />
        </DetailSection>
      )}

      {hasSide && (
        <div className="space-y-10">
          {parties.length > 0 && (
            <DetailSection
              hideTitle={Boolean(only)}
              id="case-parties"
              title="Parties"
              count={parties.length}
            >
              <FoldedList
                limit={limit}
                items={parties}
                label="parties"
                className="divide-y divide-line"
                render={(party, index) => (
                  <li key={index} className="py-5 first:pt-0">
                    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                      <p className="text-lg font-semibold text-ink [overflow-wrap:anywhere]">
                        {party.name}
                      </p>
                      <p
                        className={
                          party.role === null
                            ? "text-sm text-ink-secondary"
                            : "text-sm font-semibold text-ink"
                        }
                      >
                        {party.role === null ? "Role not identified" : party.role}
                      </p>
                    </div>
                    {party.linkedClaims?.length ? (
                      <ul aria-label={`Findings that mention ${party.name}`} className="mt-2">
                        {party.linkedClaims.map((claim) => {
                          const number = findingNumbers?.[claim.id];
                          return (
                            <li key={claim.id} className="flex min-w-0 items-baseline gap-3">
                              <span className="w-6 shrink-0 text-right font-mono text-xs font-bold text-ink-secondary">
                                {number ?? ""}
                              </span>
                              {caseId ? (
                                <Link
                                  href={findingHref(caseId, claim.id)}
                                  title={claim.text}
                                  aria-label={
                                    number ? `Finding ${number}: ${claim.text}` : claim.text
                                  }
                                  className="line-clamp-2 min-h-8 min-w-0 flex-1 py-1 text-base text-ink hover:underline hover:underline-offset-4"
                                >
                                  {claim.text}
                                </Link>
                              ) : (
                                <span className="min-w-0 flex-1 truncate py-1 text-base">
                                  {claim.text}
                                </span>
                              )}
                            </li>
                          );
                        })}
                      </ul>
                    ) : (
                      <p className="mt-2 text-sm text-ink-secondary">No finding mentions them.</p>
                    )}
                    {!party.linkedClaims?.length && backing(party, `party-${index}`, false)}
                    {Boolean(party.linkedClaims?.length) &&
                      (party.unconfirmed.length > 0 || party.supportNote) && (
                        <p className="mt-2 flex flex-wrap gap-x-3 text-xs text-ink-secondary">
                          {party.unconfirmed.map((status) => (
                            <span key={status}>{UNCONFIRMED_NOTES[status]}</span>
                          ))}
                          {party.supportNote && <span>{party.supportNote}</span>}
                        </p>
                      )}
                  </li>
                )}
              />
            </DetailSection>
          )}

          {impacts.length > 0 && (
            <DetailSection
              hideTitle={Boolean(only)}
              id="case-impacts"
              title="Impact"
              count={impacts.length}
            >
              <FoldedList
                limit={limit}
                items={impactsShown}
                label="impacts"
                className="flex flex-col gap-4"
                render={(impact, index) => {
                  const amount = amountIn(impact.description);
                  return (
                    <li
                      key={index}
                      className={
                        amount ? "rounded-xl bg-field px-5 py-4" : "border-b border-line pb-4"
                      }
                    >
                      {amount && (
                        <p className="font-mono text-3xl font-bold leading-tight text-ink [overflow-wrap:anywhere]">
                          {amount}
                        </p>
                      )}
                      <p className={`text-base text-ink ${amount ? "mt-1" : ""}`}>
                        {impact.description}
                      </p>
                      {backing(impact, `impact-${index}`)}
                    </li>
                  );
                }}
              />
            </DetailSection>
          )}
        </div>
      )}
    </div>
  );
}

function DetailSection({
  hideTitle,
  id,
  title,
  count,
  children,
}: {
  hideTitle?: boolean;
  id: string;
  title: string;
  count: number;
  children: ReactNode;
}) {
  return (
    <section aria-labelledby={`${id}-heading`} className="min-w-0">
      <h2
        hidden={hideTitle}
        id={`${id}-heading`}
        className="flex items-baseline gap-2 text-base font-semibold text-ink"
      >
        {title} <span className="text-sm font-medium text-ink-muted">{count}</span>
      </h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function FoldedList<T>({
  items,
  label,
  limit,
  as: List = "ul",
  className,
  render,
}: {
  items: T[];
  label: string;
  limit: number;
  as?: "ul" | "ol";
  className: string;
  render: (item: T, index: number) => ReactNode;
}) {
  const [expanded, setExpanded] = useState(false);
  const folds = items.length > limit;
  const shown = expanded || !folds ? items : items.slice(0, limit);

  return (
    <>
      <List className={className}>{shown.map(render)}</List>
      {folds && (
        <button
          type="button"
          onClick={() => setExpanded((open) => !open)}
          className="mt-3 text-sm font-medium text-ink-secondary hover:text-ink"
        >
          {expanded ? "Show fewer" : `Show all ${items.length}`}{" "}
          <span className="sr-only">{label}</span>
        </button>
      )}
    </>
  );
}

function Backing({
  row,
  caseId,
  owner,
  onSelectSource,
  activeSourceKey,
  findingNumbers,
  showClaims = true,
}: {
  row: ClaimBacked;
  caseId?: string;
  owner: string;
  onSelectSource: CaseDetailsProps["onSelectSource"];
  activeSourceKey: string | null;
  findingNumbers?: Record<string, number>;
  showClaims?: boolean;
}) {
  const linked = showClaims ? (row.linkedClaims ?? []) : [];
  const asLinks = Boolean(findingNumbers && caseId);
  const hasReview = linked.length > 0;
  if (!row.sources.length && !row.unconfirmed.length && !row.supportNote && !hasReview) {
    return null;
  }
  return (
    <div className="mt-2">
      <div className="flex flex-wrap items-center gap-1.5">
        {row.unconfirmed.map((status) => (
          <span key={status} className="text-xs text-ink-muted">
            {UNCONFIRMED_NOTES[status]}
          </span>
        ))}
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
        {asLinks &&
          linked.map((claim) => (
            <FindingRef
              key={claim.id}
              caseId={caseId!}
              id={claim.id}
              number={findingNumbers?.[claim.id]}
            />
          ))}
        {row.supportNote && <span className="text-xs text-ink-muted">{row.supportNote}</span>}
      </div>
      {hasReview && !asLinks && <ClaimViewReview row={row} caseId={caseId} />}
    </div>
  );
}
