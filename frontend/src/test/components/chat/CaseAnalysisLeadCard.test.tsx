import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead, PersistedChatMessage } from "@/lib/api";
import { CaseAnalysisLeadCard } from "@/components/conversation/CaseAnalysisLeadCard";
import { ChatTranscript } from "@/components/conversation/ChatTranscript";

const sampleResult: CaseAnalysisResultRead = {
  id: "analysis-result-1",
  case_id: "case-123",
  run_id: "run-123",
  snapshot_id: "snapshot-123",
  schema_version: "analysis_trace_v3",
  status: "validated",
  summary: "Initial compromise occurred via spearphishing attachment delivering malware.",
  answer: "Initial compromise occurred via spearphishing attachment delivering malware.",
  trace_json: null,
  execution_receipt_json: null,
  retrieval_context_id: null,
  pipeline_config: {},
  provider_metadata_json: {},
  created_at: "2026-09-10T12:00:00Z",
  freshness: "current",
};

const sampleSnapshot: CaseEvidenceSnapshotRead = {
  id: "snapshot-123",
  case_id: "case-123",
  evidence_revision: 1,
  format_version: "v1",
  manifest_json: [],
  input_text: "test",
  text_sha256: "hash",
  manifest_sha256: "hash",
  created_at: "2026-09-10T11:59:00Z",
};

describe("CaseAnalysisLeadCard", () => {
  it("renders grounded case analysis summary and validated pill", () => {
    const onOpenOverview = vi.fn();
    render(
      <CaseAnalysisLeadCard
        result={sampleResult}
        snapshot={sampleSnapshot}
        onOpenOverview={onOpenOverview}
      />,
    );

    expect(screen.getByText("Grounded Case Analysis")).toBeInTheDocument();
    expect(screen.getByText("Validated")).toBeInTheDocument();
    expect(
      screen.getByText("Initial compromise occurred via spearphishing attachment delivering malware."),
    ).toBeInTheDocument();

    const overviewBtn = screen.getByRole("button", { name: /view full case overview/i });
    expect(overviewBtn).toBeInTheDocument();
    fireEvent.click(overviewBtn);
    expect(onOpenOverview).toHaveBeenCalledTimes(1);
  });
});

describe("ChatTranscript with Lead Card", () => {
  it("renders lead card at the top and deduplicates matching historical publication message", () => {
    const historicalDuplicateMessage: PersistedChatMessage = {
      id: "msg-pub-1",
      thread_id: "thread-1",
      ordinal: 1,
      role: "assistant",
      content: "Duplicate publication of analysis findings",
      retrieval_context_id: null,
      analysis_result_id: "analysis-result-1",
      metadata_json: {},
      created_at: "2026-09-10T12:00:01Z",
    };

    const regularQAMessage: PersistedChatMessage = {
      id: "msg-qa-1",
      thread_id: "thread-1",
      ordinal: 2,
      role: "user",
      content: "What malware family was identified?",
      retrieval_context_id: null,
      analysis_result_id: null,
      metadata_json: {},
      created_at: "2026-09-10T12:05:00Z",
    };

    render(
      <ChatTranscript
        messages={[historicalDuplicateMessage, regularQAMessage]}
        isProcessing={false}
        leadResult={sampleResult}
        leadSnapshot={sampleSnapshot}
      />,
    );

    // Lead card is rendered
    expect(screen.getByText("Grounded Case Analysis")).toBeInTheDocument();

    // Regular QA message is rendered
    expect(screen.getByText("What malware family was identified?")).toBeInTheDocument();

    // Historical publication message matching leadResult.id is omitted from transcript
    expect(screen.queryByText("Duplicate publication of analysis findings")).not.toBeInTheDocument();
  });

  it("renders followup_question in transcript even when linked to leadResult.id", () => {
    const followupQuestionMessage: PersistedChatMessage = {
      id: "msg-followup-1",
      thread_id: "thread-1",
      ordinal: 3,
      role: "assistant",
      content: "What was the destination IP address for the exfiltration traffic?",
      message_kind: "followup_question",
      retrieval_context_id: null,
      analysis_result_id: "analysis-result-1",
      metadata_json: {
        analysis_kind: "clarification_question",
        analysis_result_id: "analysis-result-1",
        chat_followup: {
          kind: "clarification",
          action: "ask_followup",
          root_ordinal: 3,
          round: 1,
          selected_gap_detail: {
            topic: "Destination IP",
            status: "NOT_PROVIDED",
            description: "Missing destination IP for exfiltration",
            affects: "Technical attribution",
            reason: "Required to verify C2 infrastructure",
            priority: "high",
            askable: true,
          },
        },
      },
      created_at: "2026-09-10T12:06:00Z",
    };

    render(
      <ChatTranscript
        messages={[followupQuestionMessage]}
        isProcessing={false}
        leadResult={sampleResult}
        leadSnapshot={sampleSnapshot}
      />,
    );

    // Followup question content is rendered
    expect(screen.getByText("What was the destination IP address for the exfiltration traffic?")).toBeInTheDocument();
    // Action card for the gap is rendered
    expect(screen.getByText("Destination IP")).toBeInTheDocument();
  });
});
