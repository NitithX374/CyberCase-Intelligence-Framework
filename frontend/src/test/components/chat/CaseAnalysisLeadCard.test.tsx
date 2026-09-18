import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api";
import { ChatTranscript } from "@/components/conversation/ChatTranscript";

const sampleResult: CaseAnalysisResultRead = {
  id: "analysis-result-1",
  case_id: "case-123",
  run_id: "run-123",
  evidence_revision: 1,
  schema_version: "case_analysis_trace_v1",
  status: "validated",
  summary: "Initial compromise occurred via spearphishing attachment delivering malware.",
  answer: "Initial compromise occurred via spearphishing attachment delivering malware.",
  trace_json: null,
  execution_receipt_json: null,
  retrieval_context_id: null,
  pipeline_config: {},
  external_context_json: {},
  created_at: "2026-09-10T12:00:00Z",
  freshness: "current",
};

const evidenceSources: CaseSourceRead[] = [{
  id: "source-1",
  case_id: "case-123",
  source_kind: "narrative",
  document_id: null,
  origin_message_id: null,
  exact_text: "Initial compromise occurred via spearphishing attachment delivering malware.",
  provenance_json: {},
  source_metadata_json: {},
  created_at: "2026-09-10T11:59:00Z",
  archived_at: null,
}];

describe("ChatTranscript lead card", () => {
  it("shows the response indicator before the first assistant message arrives", () => {
    render(<ChatTranscript messages={[]} isProcessing={false} isResponding />);

    expect(screen.getByRole("status", { name: "CyberCase is responding" })).toBeInTheDocument();
    expect(screen.getByText("...")).toBeInTheDocument();
  });

  it("renders the exploration hint when messages are empty", () => {
    const onOpenOverview = vi.fn();
    render(<ChatTranscript messages={[]} isProcessing={false} leadResult={sampleResult} evidenceSources={evidenceSources} onOpenOverview={onOpenOverview} />);
    expect(screen.getByText("Ask a question below to explore the case analysis or review details.")).toBeInTheDocument();
  });
});

describe("ChatTranscript with Lead Card", () => {
  it("renders messages and filters historical publication", () => {
    const historicalDuplicateMessage: ChatMessageRead = {
      id: "msg-pub-1", case_id: "case-123", ordinal: 1, role: "assistant",
      content: "Duplicate publication of analysis findings", retrieval_context_id: null,
      message_kind: "conversation", analysis_result_id: "analysis-result-1", metadata_json: {},
      created_at: "2026-09-10T12:00:01Z",
    };
    const regularQAMessage: ChatMessageRead = {
      id: "msg-qa-1", case_id: "case-123", ordinal: 2, role: "user",
      content: "What malware family was identified?", retrieval_context_id: null,
      message_kind: "conversation", analysis_result_id: null, metadata_json: {},
      created_at: "2026-09-10T12:05:00Z",
    };
    render(<ChatTranscript messages={[historicalDuplicateMessage, regularQAMessage]} isProcessing={false} leadResult={sampleResult} evidenceSources={evidenceSources} />);
    expect(screen.getByText("What malware family was identified?")).toBeInTheDocument();
    expect(screen.queryByText("Duplicate publication of analysis findings")).not.toBeInTheDocument();
  });

  it("renders a follow-up question linked to the current analysis", () => {
    const followupQuestionMessage: ChatMessageRead = {
      id: "msg-followup-1", case_id: "case-123", ordinal: 3, role: "assistant",
      content: "What was the destination IP address for the exfiltration traffic?",
      message_kind: "followup_question", retrieval_context_id: null, analysis_result_id: "analysis-result-1",
      metadata_json: {
        action: "follow_up",
        chat_followup: {
          root_ordinal: 3,
          round: 1,
          source_analysis_id: "analysis-result-1",
          source_revision: 1,
          gap: {
            gap_id: "gap-destination-ip",
            gap_key: "destination_ip",
            topic: "Destination IP",
            status: "NOT_PROVIDED",
            description: "Missing destination IP for exfiltration",
            affects: "Technical attribution",
            reason: "Required to verify C2 infrastructure",
            priority: "high",
            askable: true,
            clarification_question: "What was the destination IP address for the exfiltration traffic?",
          },
        },
      },
      created_at: "2026-09-10T12:06:00Z",
    };
    render(<ChatTranscript messages={[followupQuestionMessage]} isProcessing={false} leadResult={sampleResult} evidenceSources={evidenceSources} />);
    expect(screen.getByText("What was the destination IP address for the exfiltration traffic?")).toBeInTheDocument();
    expect(screen.getByText("Destination IP")).toBeInTheDocument();
  });
});
