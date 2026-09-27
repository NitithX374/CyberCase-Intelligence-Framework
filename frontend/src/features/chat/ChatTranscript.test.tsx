import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { CaseAnalysisClaim, ChatAnswerUnit, ChatMessageRead } from "@/lib/api/types";
import {
  analysisResult,
  followupExchange,
  narrativeSource,
  pagedDocumentSource,
} from "@/test/fixtures";
import { ChatTranscript } from "./ChatTranscript";

function message(
  id: string,
  ordinal: number,
  role: "user" | "assistant",
  content: string,
  metadata: ChatMessageRead["metadata_json"] = {},
): ChatMessageRead {
  return {
    id,
    case_id: "case-123",
    ordinal,
    role,
    content,
    message_kind: "conversation",
    analysis_result_id: null,
    metadata_json: metadata,
    created_at: "2026-09-10T12:00:00Z",
  };
}

function analysisMessage(claims: Record<string, unknown>[]): ChatMessageRead {
  return message("analysis-1", 3, "assistant", "Case analysis", {
    analysis_trace: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      summary: "Case analysis",
      claims: claims as CaseAnalysisClaim[],
    },
  });
}

describe("ChatTranscript", () => {
  it("shows the exchange the analysis pinned to itself", () => {
    const [question, answer] = followupExchange(
      "When did the incident happen?",
      "Around two in the morning.",
    );
    render(
      <ChatTranscript
        messages={[question, answer]}
        isProcessing={false}
        leadResult={analysisResult()}
        sources={[narrativeSource("Initial compromise occurred via spearphishing.")]}
      />,
    );
    expect(screen.getByText("When did the incident happen?")).toBeInTheDocument();
    expect(screen.getByText("Around two in the morning.")).toBeInTheDocument();
    expect(screen.getByText("Question")).toBeInTheDocument();
  });

  it("reads assistant messages as Markdown and keeps what the reader typed as written", () => {
    render(
      <ChatTranscript
        messages={[
          message("msg-user", 1, "user", "Check this **user message** with `code`."),
          message("msg-assistant", 2, "assistant", "Here is **assistant response**."),
        ]}
        isProcessing={false}
      />,
    );

    expect(screen.getByText("Check this **user message** with `code`.")).toBeInTheDocument();
    expect(screen.getByText("assistant response").tagName).toBe("STRONG");
  });

  it("does not render raw HTML an assistant message contains", () => {
    const { container } = render(
      <ChatTranscript
        messages={[
          message(
            "msg-assistant",
            1,
            "assistant",
            `Hello <button id="unsafe-btn">Click me</button> <script>console.log('xss')</script>`,
          ),
        ]}
        isProcessing={false}
      />,
    );

    expect(container.querySelector("#unsafe-btn")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(screen.getByText(/Hello/)).toBeInTheDocument();
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
      const first = message("m-1", 1, "user", "Message 1");
      const second = message("m-2", 2, "user", "Message 2");

      const { container, rerender } = render(
        <ChatTranscript messages={[first]} isProcessing={false} />,
      );
      expect(scrolled).toEqual([]);

      rerender(<ChatTranscript messages={[first, second]} isProcessing={false} />);
      expect(scrolled).toEqual([container.firstElementChild]);
      expect(scrollIntoView).not.toHaveBeenCalled();
    });
  });
});

describe("ChatTranscript source references", () => {
  it("shows a narrative citation without inventing a page number", () => {
    const narrative = narrativeSource(
      "The witness reported seeing a blue vehicle near the entrance.",
    );
    const analysis = analysisMessage([
      {
        supporting_source_ids: [narrative.id],
        contradicting_source_ids: [],
        supporting_citations: [{ source_id: narrative.id, exact_quote: "seeing a blue vehicle" }],
        contradicting_citations: [],
      },
    ]);

    render(<ChatTranscript messages={[analysis]} isProcessing={false} sources={[narrative]} />);
    expect(screen.getByRole("button", { name: "Case narrative #1" })).toBeInTheDocument();
    expect(screen.queryByText(/p\. 1/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Case narrative #1" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("seeing a blue vehicle");
  });

  it("shows a page citation, and a follow-up answer that conflicts with it", () => {
    const statement = pagedDocumentSource("Page 4 records the transfer.", 4);
    const exchange = followupExchange(
      "Was the transfer made?",
      "No transfer was ever made.",
      "topic:transfer",
      "QA-03",
    );
    const analysis = analysisMessage([
      {
        supporting_source_ids: [statement.id],
        contradicting_source_ids: ["QA-03"],
        supporting_citations: [
          {
            source_id: statement.id,
            exact_quote: "records the transfer",
            document_id: "DOC-1",
            filename: "statement.pdf",
            page_numbers: [4],
          },
        ],
        contradicting_citations: [
          { source_id: "QA-03", exact_quote: "No transfer was ever made." },
        ],
      },
    ]);

    render(
      <ChatTranscript
        messages={[...exchange, analysis]}
        isProcessing={false}
        sources={[statement]}
      />,
    );

    expect(
      screen.getByRole("button", { name: "Conflicts with Follow-up answer QA-03" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "statement.pdf · p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("Page 4");
    expect(screen.getByRole("dialog")).toHaveTextContent("records the transfer");
  });
});

describe("ChatTranscript answer units", () => {
  function answer(units: ChatAnswerUnit[], suggestion?: "add_source" | "run_analysis") {
    return message("answer-1", 2, "assistant", units.map((unit) => unit.text).join(" "), {
      answer_units: units,
      ...(suggestion ? { suggestion } : {}),
    });
  }

  it("gives each statement the source it was quoted from, with its page", () => {
    const statement = pagedDocumentSource("Page 20 records the transfer to 123-4-56789.", 20);
    render(
      <ChatTranscript
        messages={[
          answer([
            {
              text: "The money went to 123-4-56789.",
              basis: "case_fact",
              supporting_source_ids: [statement.id],
              supporting_citations: [
                {
                  source_id: statement.id,
                  exact_quote: "transfer to 123-4-56789",
                  document_id: "DOC-1",
                  filename: "statement.pdf",
                  page_numbers: [20],
                },
              ],
            },
            { text: "Nothing names the caller.", basis: "general" },
          ]),
        ]}
        isProcessing={false}
        sources={[statement]}
      />,
    );

    expect(screen.getByText("The money went to 123-4-56789.")).toBeInTheDocument();
    expect(screen.getByText("Nothing names the caller.")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "statement.pdf · p. 20" })).toHaveLength(1);
  });

  it("marks only an interpretation as preliminary", () => {
    render(
      <ChatTranscript
        messages={[
          answer([
            { text: "The caller posed as police.", basis: "case_fact" },
            { text: "It looks like a call-centre scam.", basis: "interpretation" },
          ]),
        ]}
        isProcessing={false}
      />,
    );

    expect(screen.getAllByText("เป็นการตีความเบื้องต้น ยังไม่ได้ผ่านการวิเคราะห์")).toHaveLength(1);
  });

  it.each([
    ["add_source", "ถ้าต้องการให้ข้อมูลนี้ถูกนำไปวิเคราะห์ ให้เพิ่มเป็น source ที่หน้า Sources"],
    ["run_analysis", "กด Analyze เพื่อวิเคราะห์เคสอีกครั้ง"],
  ] as const)("tells the reader what to do next for %s", (suggestion, line) => {
    render(
      <ChatTranscript
        messages={[answer([{ text: "Noted.", basis: "general" }], suggestion)]}
        isProcessing={false}
      />,
    );

    expect(screen.getByText(line)).toBeInTheDocument();
  });
});
