"use client";

import { useState } from "react";
import type {
  ChatReportRead,
  ChatStructuredReport,
} from "@/lib/api";
import { ReportClaimInspector } from "./ReportClaimInspector";

interface PersistedReportCardProps {
  report: ChatReportRead;
  threadId: string;
  threadTitle: string;
  isDownloading: boolean;
  onDownloadPdf: () => void;
}

export function PersistedReportCard({
  report,
  threadId,
  threadTitle,
  isDownloading,
  onDownloadPdf,
}: PersistedReportCardProps) {
  return (
    <article
      aria-label="Persisted report"
      className="min-w-0 rounded-2xl border border-line-strong bg-surface p-5 shadow-[0_4px_18px_rgba(39,39,39,0.05)] sm:p-8"
    >
      <header className="border-b border-line pb-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-ink-secondary">
            Version {report.version_number} · Saved
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-line-strong bg-surface px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-[0.12em] text-ink-secondary">
              {report.persistence_status === "completed"
                ? "Provisional / Unverified"
                : "Generation failed"}
            </span>
            {report.persistence_status === "completed" && report.report && (
              <button
                type="button"
                onClick={onDownloadPdf}
                disabled={isDownloading}
                className="rounded-full border border-primary bg-primary px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-[0.12em] text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed disabled:cursor-wait disabled:border-control-disabled disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                {isDownloading ? "Preparing PDF..." : "Download PDF"}
              </button>
            )}
          </div>
        </div>
        <h2 className="mt-2 text-2xl font-extrabold tracking-[-0.03em] text-ink">
          {report.report?.title ?? threadTitle}
        </h2>
        <p className="mt-2 text-xs text-ink-secondary">
          Extraction {report.extraction_version} · {report.model}
        </p>
      </header>

      {report.persistence_status === "failed" || !report.report ? (
        <ReportFailure report={report} />
      ) : (
        <StructuredReportView report={report.report} threadId={threadId} />
      )}
    </article>
  );
}

function StructuredReportView({
  report,
  threadId,
}: {
  report: ChatStructuredReport;
  threadId: string;
}) {
  const [selectedClaimId, setSelectedClaimId] = useState(
    report.claims[0]?.claim_id ?? null,
  );
  const selectedClaim =
    report.claims.find((claim) => claim.claim_id === selectedClaimId) ??
    report.claims[0] ??
    null;
  const selectedSection = selectedClaim
    ? report.sections.find(
        (section) => section.section_id === selectedClaim.section_id,
      )
    : null;

  return (
    <>
      <div
        className={
          selectedClaim
            ? "grid gap-6 lg:grid-cols-[minmax(0,1fr)_270px]"
            : undefined
        }
      >
        <div className="divide-y divide-line">
          {report.sections.map((section) => {
            const claims = report.claims.filter(
              (claim) => claim.section_id === section.section_id,
            );
            return (
              <section key={section.section_id} className="py-6 first:pt-7 last:pb-2">
                <h3 className="text-lg font-extrabold tracking-tight text-ink">
                  {section.heading}
                </h3>
                <div className="mt-3 space-y-3 text-sm leading-6 text-ink-secondary">
                  {section.paragraphs.map((paragraph, index) => (
                    <p key={`${section.section_id}-paragraph-${index}`}>
                      {paragraph}
                    </p>
                  ))}
                </div>
                {section.items.length > 0 && (
                  <ul className="mt-4 list-disc space-y-2 pl-5 text-sm leading-6 text-ink">
                    {section.items.map((item, index) => (
                      <li key={`${section.section_id}-item-${index}`}>{item}</li>
                    ))}
                  </ul>
                )}
                {claims.length > 0 && (
                  <div className="mt-5 space-y-2" aria-label={`${section.heading} claims`}>
                    {claims.map((claim) => (
                      <button
                        key={claim.claim_id}
                        type="button"
                        aria-pressed={claim.claim_id === selectedClaim?.claim_id}
                        onClick={() => setSelectedClaimId(claim.claim_id)}
                        className={`w-full rounded-xl border p-3 text-left outline-none transition-colors focus-visible:ring-2 focus-visible:ring-primary ${
                          claim.claim_id === selectedClaim?.claim_id
                            ? "border-primary bg-surface-nested"
                            : "border-line bg-surface hover:border-line-strong"
                        }`}
                      >
                        <span className="flex flex-wrap items-center gap-2">
                          <span className="text-[10px] font-extrabold uppercase tracking-[0.1em] text-ink-secondary">
                            {claim.claim_id}
                          </span>
                          <span className="rounded-full border border-line px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.08em] text-ink-secondary">
                            {claim.support_type.replaceAll("_", " ")}
                          </span>
                        </span>
                        <span className="mt-2 block text-sm leading-6 text-ink">
                          {claim.text}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </section>
            );
          })}
        </div>
        {selectedClaim && selectedSection && (
          <div className="py-6 first:pt-7">
            <ReportClaimInspector
              claim={selectedClaim}
              sectionHeading={selectedSection.heading}
              reportStatus={report.status}
              threadId={threadId}
            />
          </div>
        )}
      </div>
      {report.report_version === "baseline_report_v1" &&
        report.limitations.length > 0 && (
          <div className="mt-6 border-t border-line pt-5">
            <h3 className="text-sm font-extrabold uppercase tracking-[0.12em] text-ink-secondary">
              Report limitations
            </h3>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-ink-secondary">
              {report.limitations.map((limitation, index) => (
                <li key={`limitation-${index}`}>{limitation}</li>
              ))}
            </ul>
          </div>
        )}
    </>
  );
}

function ReportFailure({ report }: { report: ChatReportRead }) {
  return (
    <div className="mt-6 rounded-xl border border-[#F0B8B2] bg-[#FFF6F4] p-4">
      <h3 className="text-sm font-extrabold text-[#B42318]">
        Report generation failed
      </h3>
      <p className="mt-2 text-sm leading-6 text-ink-secondary">
        {report.failure_message ?? "The backend did not produce a validated report."}
      </p>
      {report.failure_code && (
        <p className="mt-2 text-xs font-bold uppercase tracking-[0.1em] text-[#B42318]">
          Failure code: {report.failure_code}
        </p>
      )}
      {report.validation_errors.length > 0 && (
        <ul className="mt-3 list-disc space-y-1 pl-5 text-xs leading-5 text-ink-secondary">
          {report.validation_errors.map((error, index) => (
            <li key={`validation-error-${index}`}>{error}</li>
          ))}
        </ul>
      )}
      <p className="mt-4 text-sm font-semibold text-ink">
        Resolve the issue, then generate another version. This failed attempt is
        preserved in report history.
      </p>
    </div>
  );
}
