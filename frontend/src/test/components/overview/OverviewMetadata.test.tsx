import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import { caseOverviewMetadata } from "@/lib/case-overview-metadata";
import { buildCaseOverview } from "@/lib/case-overview";
import { sourceMessage, analysisMessage } from "./overview-fixtures";

describe("Overview metadata and summary", () => {
  it("counts only case evidence and distinct real documents, and identifies newer material", () => {
    const original = sourceMessage("source-1", 1, "Original statement");
    original.metadata_json.document_sources = [
      { document_id: "doc-1", filename: "statement.pdf" },
      { document_id: "doc-2", filename: "receipt.pdf" },
    ];
    const extra = sourceMessage("source-2", 4, "Additional statement");
    extra.metadata_json.document_sources = [{ document_id: "doc-1", filename: "statement.pdf" }];
    const ask = sourceMessage("ask", 5, "Is this complete?");
    ask.metadata_json = { evidence_kind: "analyst_question", document_sources: [{ document_id: "fake", filename: "exclude.pdf" }] };
    const messages = [original, analysisMessage(false), extra, ask];
    const overview = buildCaseOverview(messages, "answered");
    expect(caseOverviewMetadata(messages, overview)).toMatchObject({
      evidenceCount: 2, hasNewMaterial: true, createdAt: "2026-08-23T10:03:00Z", citedSourceCount: 2,
      documents: [{ id: "doc-1", filename: "statement.pdf" }, { id: "doc-2", filename: "receipt.pdf" }],
    });
  });

  it("preserves the summary, shows a compact empty gap state and reveals the complete long title", () => {
    const summary = "ข้อความสรุปเดิม: ไม่ปรากฏข้อมูลยืนยันเพิ่มเติม — 52,000 บาท";
    const analysis = analysisMessage(false);
    analysis.metadata_json.analysis_trace = { ...(analysis.metadata_json.analysis_trace as Record<string, unknown>), summary, gaps: [] };
    const longTitle = "ชื่อคดีพร้อมรายละเอียดตามเอกสารต้นฉบับ ".repeat(12);
    render(<CaseOverviewView threadId="thread-1" threadTitle={longTitle} threadStatus="answered"
      messages={[sourceMessage("source-1", 1, "Statement"), analysis]} onOpenChat={vi.fn()} onOpenReport={vi.fn()} />);
    expect(screen.getByText(summary)).toBeVisible();
    expect(screen.getByText("No open questions recorded.")).toBeVisible();
    expect(screen.queryByRole("button", { name: /Clarify in Chat/ })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toHaveClass("line-clamp-2");
    fireEvent.click(screen.getByRole("button", { name: "Read full title" }));
    expect(screen.getByRole("heading", { level: 1 })).not.toHaveClass("line-clamp-2");
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe(longTitle);
    expect(screen.queryByText(/Ready for report|Case version|100%/)).not.toBeInTheDocument();
  });
});
