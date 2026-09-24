import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api";
import { ChatTranscript } from "./ChatTranscript";

const sampleResult: CaseAnalysisResultRead = {
  id: "analysis-result-1",
  case_id: "case-123",
  source_revision: 1,
  schema_version: "case_analysis_trace_v1",
  status: "validated",
  summary: "Initial compromise occurred via spearphishing attachment delivering malware.",
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
    exact_text: "Initial compromise occurred via spearphishing attachment delivering malware.",
    provenance_json: {},
    source_metadata_json: {},
    created_at: "2026-09-10T11:59:00Z",
    archived_at: null,
  },
];

describe("ChatTranscript", () => {
  it("shows the exchange the analysis pinned to itself", () => {
    const question: ChatMessageRead = {
      id: "msg-q-1",
      case_id: "case-123",
      ordinal: 1,
      role: "assistant",
      content: "When did the incident happen?",
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
    expect(screen.getByText("Question")).toBeInTheDocument();
  });

  describe("scrolling", () => {
    afterEach(() => {
      delete (HTMLElement.prototype as Partial<HTMLElement>).scrollTo;
      delete (Element.prototype as Partial<Element>).scrollIntoView;
    });

    it("brings a new message into view by scrolling the transcript alone", () => {
      const scrolled: Element[] = [];
      Object.defineProperty(HTMLElement.prototype, "scrollTo", {
        configurable: true,
        value(this: HTMLElement) {
          scrolled.push(this);
        },
      });
      const scrollIntoView = vi.fn();
      Object.defineProperty(Element.prototype, "scrollIntoView", {
        configurable: true,
        value: scrollIntoView,
      });
      const message = (id: string, ordinal: number): ChatMessageRead => ({
        id,
        case_id: "case-123",
        ordinal,
        role: "user",
        content: `Message ${ordinal}`,
        message_kind: "conversation",
        analysis_result_id: null,
        metadata_json: {},
        created_at: "2026-09-10T12:00:00Z",
      });

      const { container, rerender } = render(
        <ChatTranscript messages={[message("m-1", 1)]} isProcessing={false} />,
      );
      expect(scrolled).toEqual([]);

      rerender(
        <ChatTranscript messages={[message("m-1", 1), message("m-2", 2)]} isProcessing={false} />,
      );
      expect(scrolled).toEqual([container.firstElementChild]);
      expect(scrollIntoView).not.toHaveBeenCalled();
    });
  });
});
