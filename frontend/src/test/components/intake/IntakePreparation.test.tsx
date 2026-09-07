import { fireEvent, render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import type { PersistedChatMessage } from "@/lib/api";
import { resetDocumentIngestionState, setDocumentIngestionFile, setDocumentIngestionResult } from "@/lib/document-ingestion-store";

const evidence: PersistedChatMessage = {
  id: "source", thread_id: "saved-case", ordinal: 1, role: "user",
  content: "<table><tr><td>Reported amount</td><td>500</td></tr></table>",
  retrieval_context_id: null, created_at: "2026-09-03T00:00:00Z",
  metadata_json: { evidence_kind: "initial_case_narrative", document_sources: [{ document_id: "DOC-1", filename: "statement.pdf", page_count: 18 }] },
};
const analysis: PersistedChatMessage = {
  ...evidence, id: "analysis", ordinal: 2, role: "assistant", content: "Analysis response",
  metadata_json: {
    analysis_trace: {
      version: "analysis_trace_v3", validation_status: "validated", analysis_mode: "case_overview",
      summary: "The material reports an amount of 500.",
      claims: ["A-01", "A-02"].map((claim_id) => ({
        claim_id, text: `Finding ${claim_id}`, claim_type: "reported", epistemic_status: "reported",
        supporting_source_message_ids: ["source"], contradicting_source_message_ids: [],
      })),
      gaps: [{ gap_id: "G-01", topic: "Date", description: "No date provided", reason: "Timing is unclear", status: "NOT_PROVIDED", priority: "high", askable: true }],
    },
  },
};

describe("Case preparation workflow", () => {
  beforeEach(() => resetDocumentIngestionState());

  it("shows real analysis fields and one primary continuation for a saved case", () => {
    const onOverview = vi.fn();
    render(<CaseIntakeView messages={[evidence, analysis]} threadStatus="answered" isSubmitting={false} onSubmitCase={vi.fn()} onOpenOverview={onOverview} onOpenChat={vi.fn()} />);
    expect(screen.getByRole("status")).toHaveTextContent("Analysis available");
    expect(screen.getByLabelText("Case narrative text")).toHaveTextContent("Reported amount | 500");
    const summary = screen.getByRole("region", { name: "Extracted case information" });
    expect(within(summary).getByText("Findings").nextElementSibling).toHaveTextContent("2");
    expect(within(summary).getByText("Evidence messages").nextElementSibling).toHaveTextContent("1");
    expect(within(summary).getByText("Open questions").nextElementSibling).toHaveTextContent("1");
    expect(screen.getByText("18 pages")).toBeInTheDocument();
    expect(screen.queryByText("Entities")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Chat/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Continue to Analysis/ }));
    expect(onOverview).toHaveBeenCalledOnce();
  });

  it("does not manufacture extracted counts from a question-answer response", () => {
    const questionResponse: PersistedChatMessage = { ...analysis, metadata_json: { ...analysis.metadata_json, analysis_state_scope: "response_scoped" } };
    render(<CaseIntakeView messages={[evidence, questionResponse]} isSubmitting={false} onSubmitCase={vi.fn()} />);
    expect(screen.getByText(/Findings and open questions become available after case analysis/)).toBeInTheDocument();
    expect(screen.queryByText("Evidence messages")).not.toBeInTheDocument();
  });

  it("keeps pending previews out of the saved case record", () => {
    setDocumentIngestionFile(new File(["pdf"], "additional.pdf"), "saved-case");
    setDocumentIngestionResult({ document_id: "DOC-2", filename: "additional.pdf", media_type: "application/pdf", extraction_method: "native_pdf", mode: "unified", full_text: "Additional information", pages: [], warnings: [] }, "saved-case");
    const submit = vi.fn();
    render(<CaseIntakeView messages={[evidence, analysis]} isSubmitting={false} onSubmitCase={submit} onOpenChat={vi.fn()} />);
    expect(screen.getByRole("status")).toHaveTextContent("Review required");
    expect(screen.getByText(/has not been added to the saved case/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Use reviewed text" })).not.toBeInTheDocument();
    expect(submit).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "statement.pdf" }));
    expect(screen.getByLabelText("Case narrative text")).toHaveTextContent("Reported amount");
  });

  it.each([
    ["processing", true, "Analyzing case…"],
    ["failed", false, "Analysis needs attention"],
  ] as const)("communicates the %s analysis state", (threadStatus, isSubmitting, expected) => {
    render(<CaseIntakeView messages={[evidence]} threadStatus={threadStatus} isSubmitting={isSubmitting} onSubmitCase={vi.fn()} onOpenChat={vi.fn()} />);
    expect(screen.getByRole("status")).toHaveTextContent(expected);
  });
});
