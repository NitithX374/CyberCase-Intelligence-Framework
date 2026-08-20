import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PersistedReportCard } from "@/components/report/PersistedReportCard";
import type { ChatReportRead } from "@/lib/api";

function reportWithClaims(): ChatReportRead {
  return {
    report_id: "report-1",
    thread_id: "thread-1",
    version_number: 1,
    idempotency_key: "report-request-1",
    source_snapshot_hash: "snapshot-1",
    extraction_id: "extraction-1",
    extraction_version: "baseline_extraction_v1",
    prompt_version: "chat_report_prompt_v1",
    provider: "openrouter",
    model: "openai/gpt-5.6-luna",
    decoding_settings: {},
    persistence_status: "completed",
    validation_status: "validated",
    report: {
      report_version: "baseline_report_v1",
      status: "provisional_unverified",
      title: "Traceable report",
      sections: [
        {
          section_id: "evidence_findings",
          heading: "Evidence Findings",
          paragraphs: ["Reported findings remain unverified."],
          items: [],
        },
        {
          section_id: "technical_analysis_mitre",
          heading: "Technical Analysis and MITRE ATT&CK Mapping",
          paragraphs: [],
          items: [],
        },
      ],
      claims: [
        {
          claim_id: "C-001",
          section_id: "evidence_findings",
          text: "A login event was reported.",
          support_type: "user_reported",
          evidence_ids: ["E-010"],
          timeline_event_ids: ["T-010"],
          mitre_technique_ids: [],
        },
        {
          claim_id: "C-002",
          section_id: "technical_analysis_mitre",
          text: "Valid Accounts is a candidate mapping.",
          support_type: "mitre_mapping_candidate",
          evidence_ids: ["E-010"],
          timeline_event_ids: [],
          mitre_technique_ids: ["T1078"],
        },
      ],
      limitations: ["This report is provisional and unverified."],
    },
    validation_errors: [],
    failure_code: null,
    failure_message: null,
    created_at: "2026-08-20T00:00:00Z",
    finished_at: "2026-08-20T00:00:01Z",
    latency_ms: 1,
    input_tokens: 1,
    output_tokens: 1,
  };
}

function renderReport(report = reportWithClaims()) {
  render(
    <PersistedReportCard
      report={report}
      threadId="thread-1"
      threadTitle="Investigation"
      isDownloading={false}
      onDownloadPdf={vi.fn()}
    />,
  );
}

describe("PersistedReportCard claim inspector", () => {
  it("shows persisted provenance and a case-evidence navigation hook", () => {
    renderReport();

    const inspector = screen.getByRole("complementary", {
      name: "Claim inspector C-001",
    });
    expect(
      within(inspector).getByText("Evidence Findings · evidence_findings"),
    ).toBeInTheDocument();
    expect(within(inspector).getAllByText("user reported")).toHaveLength(2);
    expect(within(inspector).getByText("T-010")).toBeInTheDocument();
    expect(within(inspector).getByText("provisional unverified")).toBeInTheDocument();
    expect(within(inspector).getByRole("link", { name: "E-010" })).toHaveAttribute(
      "href",
      "/chat/thread-1/extraction#case-reference-E-010",
    );
  });

  it("switches the inspector to the selected claim without strengthening it", () => {
    renderReport();

    fireEvent.click(
      screen.getByRole("button", {
        name: /C-002.*Valid Accounts is a candidate mapping/i,
      }),
    );

    const inspector = screen.getByRole("complementary", {
      name: "Claim inspector C-002",
    });
    expect(within(inspector).getByText("T1078")).toBeInTheDocument();
    expect(within(inspector).getAllByText("mitre mapping candidate")).toHaveLength(2);
    expect(
      within(inspector).getByText(/MITRE mappings remain external candidate context/i),
    ).toBeInTheDocument();
  });

  it("keeps a legacy report without claims readable", () => {
    const report = reportWithClaims();
    if (!report.report) throw new Error("report fixture is required");
    report.report = { ...report.report, claims: [] };

    renderReport(report);

    expect(screen.getByText("Reported findings remain unverified.")).toBeInTheDocument();
    expect(screen.getByText("This report is provisional and unverified.")).toBeInTheDocument();
    expect(screen.queryByText("Claim inspector")).not.toBeInTheDocument();
  });
});
