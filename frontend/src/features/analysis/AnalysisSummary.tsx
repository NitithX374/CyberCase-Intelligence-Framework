"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCaseReports } from "@/features/reports/queries";
import { Markdown } from "@/components/Markdown";
import { analysisPath } from "@/lib/casePaths";
import {
  buildTechnicalContext,
  technicalContextMessage,
} from "./technical-context/technicalContext";
import type { EpistemicStatus } from "./types";
import { useCaseOverview } from "./useCaseOverview";

const statusWords: Record<EpistemicStatus, string> = {
  reported: "reported",
  not_confirmed: "not confirmed",
  not_established: "not established",
  suspected: "suspected",
  contradicted: "contradicted",
  unknown: "unknown",
};

const statusOrder: EpistemicStatus[] = [
  "reported",
  "not_confirmed",
  "not_established",
  "suspected",
  "contradicted",
  "unknown",
];

const PARTIES_SHOWN = 3;
const IMPACTS_SHOWN = 2;

export function AnalysisSummary() {
  const { caseId } = useParams<{ caseId: string }>();
  const { analysisResult, sources, overview } = useCaseOverview(caseId);
  const reports = useCaseReports(caseId).data ?? [];
  if (!analysisResult || !overview.hasAnalysis) return null;

  const technical = buildTechnicalContext(analysisResult, sources);
  const { parties, timeline, impacts, findings, gaps } = overview;
  const statusCounts = statusOrder
    .map((status) => ({
      status,
      count: findings.filter((finding) => finding.epistemicStatus === status).length,
    }))
    .filter((entry) => entry.count > 0);
  const events = timeline.length > 1 ? [timeline[0], timeline[timeline.length - 1]] : timeline;
  const latestReport = reports[0] ?? null;

  return (
    <div className="mx-auto w-full max-w-[52rem] px-5 pt-8 sm:px-8">
      <section aria-labelledby="overview-summary-heading" className="min-w-0">
        <h2 id="overview-summary-heading" className="text-base font-semibold text-ink">
          Summary
        </h2>
        <div className="mt-3 max-w-[68ch] text-ink [overflow-wrap:anywhere] [&_p]:mb-4 [&_p]:text-base [&_p]:leading-8 sm:[&_p]:text-[17px]">
          <Markdown content={overview.incidentSummary} />
        </div>
      </section>

      <section aria-labelledby="overview-glance-heading" className="mt-8">
        <h2 id="overview-glance-heading" className="text-base font-semibold text-ink">
          At a glance
        </h2>
        <dl className="mt-2 divide-y divide-line border-y border-line">
          {parties.length > 0 && (
            <GlanceRow label="Parties">
              {parties.slice(0, PARTIES_SHOWN).map((party, index) => (
                <p key={index}>
                  {party.name} <span className="text-ink-secondary">{party.role}</span>
                </p>
              ))}
              {parties.length > PARTIES_SHOWN && (
                <TabLink href={analysisPath(caseId, "details")}>
                  All {parties.length} parties
                </TabLink>
              )}
            </GlanceRow>
          )}

          {events.length > 0 && (
            <GlanceRow label={timeline.length > 1 ? "From first to last" : "When"}>
              {events.map((event, index) => (
                <p key={index}>
                  <span className="text-ink-secondary">{event.time}</span> {event.event}
                </p>
              ))}
              {timeline.length > events.length && (
                <TabLink href={analysisPath(caseId, "details")}>
                  All {timeline.length} events
                </TabLink>
              )}
            </GlanceRow>
          )}

          {impacts.length > 0 && (
            <GlanceRow label="Impact">
              {impacts.slice(0, IMPACTS_SHOWN).map((impact, index) => (
                <p key={index}>{impact.description}</p>
              ))}
              {impacts.length > IMPACTS_SHOWN && (
                <TabLink href={analysisPath(caseId, "details")}>
                  All {impacts.length} impacts
                </TabLink>
              )}
            </GlanceRow>
          )}

          <GlanceRow label="Findings">
            <p>
              <Link
                href={analysisPath(caseId, "findings")}
                className="font-semibold hover:underline"
              >
                {findings.length} {findings.length === 1 ? "finding" : "findings"}
              </Link>
              {statusCounts.map(({ status, count }) => (
                <span key={status}>
                  {", "}
                  {status === "not_confirmed" ? (
                    <Link
                      href={`${analysisPath(caseId, "findings")}?status=not_confirmed`}
                      className="text-unresolved hover:underline"
                    >
                      {count} {statusWords[status]}
                    </Link>
                  ) : (
                    <span className="text-ink-secondary">
                      {count} {statusWords[status]}
                    </span>
                  )}
                </span>
              ))}
            </p>
          </GlanceRow>

          <GlanceRow label="Open questions">
            {gaps.length === 0 ? (
              <p className="text-ink-secondary">Nothing is missing from this analysis.</p>
            ) : (
              <>
                <p>{gaps[0].description}</p>
                <TabLink href={analysisPath(caseId, "questions")}>
                  {gaps.length === 1 ? "Open question" : `All ${gaps.length} open questions`}
                </TabLink>
              </>
            )}
          </GlanceRow>

          <GlanceRow label="ATT&CK">
            {technical.techniques.length > 0 ? (
              <p>
                {technical.techniques
                  .slice(0, 3)
                  .map((item) => item.techniqueId)
                  .join(", ")}
                {technical.techniques.length > 3 && ` and ${technical.techniques.length - 3} more`}
              </p>
            ) : (
              <p className="text-ink-secondary">{technicalContextMessage(technical)}</p>
            )}
            <TabLink href={analysisPath(caseId, "details")}>ATT&amp;CK context</TabLink>
          </GlanceRow>

          <GlanceRow label="Report">
            <p className={latestReport ? undefined : "text-ink-secondary"}>
              {latestReport
                ? `Version ${latestReport.version_number}, ${
                    latestReport.analysis_result_id === analysisResult.id
                      ? "from this analysis"
                      : "from an earlier analysis"
                  }`
                : "No report yet."}
            </p>
            <TabLink href={analysisPath(caseId, "report")}>
              {latestReport ? "Open the report" : "Generate a report"}
            </TabLink>
          </GlanceRow>
        </dl>
      </section>
    </div>
  );
}

function GlanceRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="grid gap-x-6 gap-y-1 py-4 sm:grid-cols-[9rem_minmax(0,1fr)]">
      <dt className="text-[13px] font-medium text-ink-secondary sm:pt-0.5">{label}</dt>
      <dd className="min-w-0 space-y-1 text-[15px] leading-7 text-ink [overflow-wrap:anywhere]">
        {children}
      </dd>
    </div>
  );
}

function TabLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link
      href={href}
      className="inline-block text-[13px] font-medium text-ink-secondary underline decoration-line-strong underline-offset-2 hover:text-ink"
    >
      {children}
    </Link>
  );
}
