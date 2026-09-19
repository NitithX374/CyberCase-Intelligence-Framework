import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api";
import { ChatTranscript } from "@/components/chat/ChatTranscript";

const sampleResult: CaseAnalysisResultRead = {
  id: "analysis-result-1",
  case_id: "case-123",
  source_revision: 1,
  schema_version: "case_analysis_trace_v1",
  status: "validated",
  summary: "Initial compromise occurred via spearphishing attachment delivering malware.",
  answer: "Initial compromise occurred via spearphishing attachment delivering malware.",
  trace_json: null,
  retrieval_context_id: null,
  pipeline_config: {},
  external_context_json: {},
  created_at: "2026-09-10T12:00:00Z",
  freshness: "current",
};

const sources: CaseSourceRead[] = [
  {
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
  },
];

describe("ChatTranscript", () => {
  it("shows the exchange the analysis pinned to itself", () => {
    // A question and its answer both carry the analysis that asked, which an
    // old filter took for a duplicate of the lead card and hid.
    const question: ChatMessageRead = {
      id: "msg-q-1",
      case_id: "case-123",
      ordinal: 1,
      role: "assistant",
      content: "When did the incident happen?",
      retrieval_context_id: null,
      message_kind: "conversation",
      analysis_result_id: "analysis-result-1",
      gap_key: "topic:incident-time",
      metadata_json: {},
      created_at: "2026-09-10T12:00:01Z",
    };
    const answer: ChatMessageRead = {
      id: "msg-a-1",
      case_id: "case-123",
      ordinal: 2,
      role: "user",
      content: "Around two in the morning.",
      retrieval_context_id: null,
      message_kind: "conversation",
      analysis_result_id: "analysis-result-1",
      in_reply_to_message_id: "msg-q-1",
      metadata_json: {},
      created_at: "2026-09-10T12:05:00Z",
    };
    render(
      <ChatTranscript
        messages={[question, answer]}
        isProcessing={false}
        leadResult={sampleResult}
        sources={sources}
      />,
    );
    expect(screen.getByText("When did the incident happen?")).toBeInTheDocument();
    expect(screen.getByText("Around two in the morning.")).toBeInTheDocument();
    expect(screen.getByText("CyberCase · One more detail")).toBeInTheDocument();
  });
});
