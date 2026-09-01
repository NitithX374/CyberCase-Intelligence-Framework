import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import { AnalysisEvidenceReferences } from "@/components/conversation/AnalysisEvidenceReferences";

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
});
