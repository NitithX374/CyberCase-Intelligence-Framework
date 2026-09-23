import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { CaseSourceRead, ChatMessageRead } from "@/lib/api";
import { ChatTranscript } from "./ChatTranscript";

function message(
  id: string,
  role: "user" | "assistant",
  content: string,
  metadata: Record<string, unknown>,
): ChatMessageRead {
  return {
    id,
    case_id: "caseChat-1",
    ordinal: role === "user" ? 1 : 2,
    role,
    content,
    message_kind: "conversation",
    analysis_result_id: null,
    metadata_json: metadata,
    created_at: "2026-09-01T00:00:00Z",
  };
}

function source(
  id: string,
  exactText: string,
  sourceKind: string,
  documentId: string | null = null,
  filename: string | null = null,
  pageNumber: number | null = null,
): CaseSourceRead {
  return {
    id,
    case_id: "caseChat-1",
    source_kind: sourceKind,
    document_id: documentId,
    origin_message_id: null,
    exact_text: exactText,
    provenance_json:
      pageNumber === null
        ? {}
        : { pages: [{ page_number: pageNumber, start_offset: 0, end_offset: exactText.length }] },
    source_metadata_json: filename ? { filename } : {},
    created_at: "2026-09-01T00:00:00Z",
    archived_at: null,
  };
}

describe("ChatTranscript source references", () => {
  it("shows a narrative citation without inventing a page number", () => {
    const narrative = source(
      "source-1",
      "The witness reported seeing a blue vehicle near the entrance.",
      "narrative",
    );
    const analysis = message("analysis-1", "assistant", "Case analysis", {
      analysis_trace: {
        version: "case_analysis_trace_v1",
        validation_status: "validated",
        claims: [
          {
            supporting_source_ids: ["source-1"],
            contradicting_source_ids: [],
            supporting_citations: [
              {
                source_id: "source-1",
                exact_quote: "seeing a blue vehicle",
                document_id: null,
                filename: null,
                page_numbers: [],
              },
            ],
            contradicting_citations: [],
          },
        ],
      },
    });

    render(<ChatTranscript messages={[analysis]} isProcessing={false} sources={[narrative]} />);
    expect(screen.getByRole("button", { name: "Case narrative #1" })).toBeInTheDocument();
    expect(screen.queryByText(/p\. 1/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Case narrative #1" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("seeing a blue vehicle");
    expect(screen.getByRole("dialog").querySelector("mark")).not.toBeInTheDocument();
  });

  it("shows page-first supporting and conflicting references", () => {
    const supporting = source(
      "source-1",
      "Page 4 records the transfer.",
      "document",
      "DOC-1",
      "statement.pdf",
      4,
    );
    const conflicting = source(
      "source-2",
      "Page 5 disputes the transfer.",
      "followup_answer",
      "DOC-2",
      "rebuttal.pdf",
      5,
    );
    const analysis = message("analysis-1", "assistant", "Case analysis", {
      analysis_trace: {
        version: "case_analysis_trace_v1",
        validation_status: "validated",
        claims: [
          {
            supporting_source_ids: ["source-1"],
            contradicting_source_ids: ["source-2"],
            supporting_citations: [
              citation("records the transfer", "source-1", "DOC-1", "statement.pdf", 4),
            ],
            contradicting_citations: [
              citation("disputes the transfer", "source-2", "DOC-2", "rebuttal.pdf", 5),
            ],
          },
        ],
      },
    });

    render(
      <ChatTranscript
        messages={[analysis]}
        isProcessing={false}
        sources={[supporting, conflicting]}
      />,
    );

    expect(screen.getByRole("button", { name: "statement.pdf · p. 4" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Conflicts with rebuttal.pdf · p. 5" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "statement.pdf · p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("Page 4");
    expect(screen.getByRole("dialog")).toHaveTextContent("records the transfer");
  });
});

function citation(
  exactQuote: string,
  sourceId: string,
  documentId: string,
  filename: string,
  pageNumber: number,
) {
  return {
    source_id: sourceId,
    exact_quote: exactQuote,
    document_id: documentId,
    filename,
    page_numbers: [pageNumber],
  };
}
