import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { CaseSourceRead } from "@/lib/api";
import { caseId, followupExchange } from "@/test/fixtures";
import { chatFollowups } from "./followupSources";
import { claimRefs, parseCaseSources } from "./sourceRefs";
import { SourceDrawer } from "./SourceDrawer";

function caseSource(id: string, kind: "narrative" | "document", filename?: string): CaseSourceRead {
  return {
    id,
    case_id: caseId,
    source_kind: kind,
    document_id: kind === "document" ? `document-${id}` : null,
    filename: filename ?? null,
    exact_text: `Text of ${id}.`,
    provenance_json: {},
    source_metadata_json: {},
    created_at: "2026-09-24T13:00:00Z",
  };
}

const messages = followupExchange("Was a warrant issued?", "No.", "arrest_warrant");

describe("SourceDrawer", () => {
  it("shows a follow-up answer with the question it answers, named by its QA id", () => {
    const sources = parseCaseSources(
      [caseSource("narrative-1", "narrative")],
      chatFollowups(messages),
    );
    const [answer] = claimRefs({ supporting_source_ids: ["QA-01"] }, sources).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    render(<SourceDrawer sourceRef={answer} anchorElement={anchor} onClose={vi.fn()} />);

    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent(
      /^Source: Follow-up answer QA-01$/,
    );
    const terms = screen.getAllByRole("term").map((term) => term.textContent);
    const definitions = screen.getAllByRole("definition").map((item) => item.textContent);
    expect(terms).toEqual(["Question", "Answer"]);
    expect(definitions).toEqual(["Was a warrant issued?", "No."]);
  });

  it("numbers a narrative among narratives, not among every source", () => {
    const sources = parseCaseSources(
      [
        caseSource("document-1", "document", "statement.pdf"),
        caseSource("narrative-1", "narrative"),
        caseSource("narrative-2", "narrative"),
      ],
      [],
    );

    const labels = claimRefs(
      { supporting_source_ids: ["document-1", "narrative-1", "narrative-2"] },
      sources,
    ).supporting.map((source) => source.label);

    expect(labels).toEqual(["statement.pdf", "Case narrative #1", "Case narrative #2"]);
  });
});
