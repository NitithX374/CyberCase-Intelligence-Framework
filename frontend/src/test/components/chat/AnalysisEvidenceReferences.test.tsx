import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import { AnalysisEvidenceReferences } from "@/components/conversation/AnalysisEvidenceReferences";
import { sha256Hex } from "@/lib/sha256";

function message(
  id: string,
  role: "user" | "assistant",
  content: string,
  metadata: Record<string, unknown>,
): PersistedChatMessage {
  return {
    id,
    thread_id: "thread-1",
    ordinal: role === "user" ? 1 : 2,
    role,
    content,
    retrieval_context_id: null,
    metadata_json: metadata,
    created_at: "2026-09-01T00:00:00Z",
  };
}

describe("AnalysisEvidenceReferences", () => {
  it("shows a narrative citation without inventing a page number", () => {
    const source = message(
      "source-1",
      "user",
      "The witness reported seeing a blue vehicle near the entrance.",
      { evidence_kind: "initial_case_narrative" },
    );
    const analysis = message("analysis-1", "assistant", "Case analysis", {
      analysis_trace: {
        version: "analysis_trace_v3",
        validation_status: "validated",
        claims: [{
          supporting_source_message_ids: ["source-1"],
          contradicting_source_message_ids: [],
          supporting_citations: [{
            source_message_id: "source-1",
            exact_quote: "seeing a blue vehicle",
            document_id: null,
            filename: null,
            page_numbers: [],
          }],
          contradicting_citations: [],
        }],
      },
    });

    render(
      <AnalysisEvidenceReferences
        analysisMessage={analysis}
        messages={[source, analysis]}
      />,
    );
    expect(screen.getByRole("button", { name: "Case narrative" })).toBeInTheDocument();
    expect(screen.queryByText(/p\. 1/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Case narrative" }));
    expect(screen.getByText("seeing a blue vehicle").tagName).toBe("MARK");
  });

  it("shows page-first supporting and conflicting references", () => {
    const supportingContent = "Page 4 records the transfer.";
    const conflictingContent = "Page 5 disputes the transfer.";
    const supporting = message("source-1", "user", supportingContent, {
      evidence_kind: "initial_case_narrative",
      document_sources: [{
        document_id: "DOC-1",
        filename: "statement.pdf",
        page_spans: [{
          page_number: 4,
          start_offset: 0,
          end_offset: supportingContent.length,
          text_sha256: sha256Hex(supportingContent),
        }],
      }],
    });
    const conflicting = message("source-2", "user", conflictingContent, {
      evidence_kind: "clarification_answer",
      document_sources: [{
        document_id: "DOC-2",
        filename: "rebuttal.pdf",
        page_spans: [{
          page_number: 5,
          start_offset: 0,
          end_offset: conflictingContent.length,
          text_sha256: sha256Hex(conflictingContent),
        }],
      }],
    });
    const analysis = message("analysis-1", "assistant", "Case analysis", {
      analysis_trace: {
        version: "analysis_trace_v3",
        validation_status: "validated",
        claims: [{
          supporting_source_message_ids: ["source-1"],
          contradicting_source_message_ids: ["source-2"],
          supporting_citations: [citation("records the transfer", "source-1", "DOC-1", "statement.pdf", 4)],
          contradicting_citations: [citation("disputes the transfer", "source-2", "DOC-2", "rebuttal.pdf", 5)],
        }],
      },
    });

    render(
      <AnalysisEvidenceReferences
        analysisMessage={analysis}
        messages={[supporting, conflicting, analysis]}
      />,
    );

    expect(screen.getByRole("button", { name: "p. 4" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Conflict · p. 5" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("Page 4");
    expect(screen.getByRole("dialog")).toHaveTextContent("records the transfer");
  });
});

function citation(
  exactQuote: string,
  sourceMessageId: string,
  documentId: string,
  filename: string,
  pageNumber: number,
) {
  return {
    source_message_id: sourceMessageId,
    exact_quote: exactQuote,
    document_id: documentId,
    filename,
    page_numbers: [pageNumber],
  };
}
