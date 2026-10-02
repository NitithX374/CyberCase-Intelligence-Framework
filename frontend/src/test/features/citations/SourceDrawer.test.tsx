import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { CaseSourceCitation, CaseSourceRead } from "@/lib/api/types";
import { caseId, followupExchange } from "@/test/fixtures";
import { chatFollowups } from "@/features/citations/followupSources";
import { claimRefs, parseCaseSources } from "@/features/citations/sourceRefs";
import { SourceDrawer } from "@/features/citations/SourceDrawer";

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

  const narrative = {
    ...caseSource("narrative-1", "narrative"),
    exact_text:
      "The victim called the bank. The caller said the account had been frozen. " +
      "He asked for a transfer of 52,000 baht to a safe account.",
  };

  function openCited(citation: CaseSourceCitation) {
    const [cited] = claimRefs(
      { supporting_source_ids: ["narrative-1"], supporting_citations: [citation] },
      parseCaseSources([narrative], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));
    render(<SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />);
    return screen.getByRole("heading", { level: 3, name: "Quoted" })
      .nextElementSibling as HTMLElement;
  }

  it("shows the quotation inside the sentence it was cut from", () => {
    const quoted = openCited({
      source_id: "narrative-1",
      exact_quote: "a transfer of 52,000 baht",
      context: {
        before: "The caller said the account had been frozen. He asked for ",
        after: " to a safe account.",
        cut_before: false,
        cut_after: false,
      },
    });

    expect(quoted).toHaveTextContent(
      /^The caller said the account had been frozen\. He asked for a transfer of 52,000 baht to a safe account\.$/,
    );
    expect(within(quoted).getByText("a transfer of 52,000 baht").tagName).toBe("STRONG");
    expect(
      screen.getAllByRole("heading", { level: 3 }).map((heading) => heading.textContent),
    ).toEqual(["Quoted", "Source text"]);
  });

  it("names a near passage as the nearest passage, not as a quotation", () => {
    const [cited] = claimRefs(
      {
        supporting_source_ids: ["narrative-1"],
        supporting_citations: [
          { source_id: "narrative-1", exact_quote: "a transfer of 52,000 baht" },
        ],
      },
      parseCaseSources([narrative], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    render(
      <SourceDrawer
        sourceRef={{ ...cited, quoteLabel: "Nearest passage" }}
        anchorElement={anchor}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { level: 3, name: "Nearest passage" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { level: 3, name: "Quoted" })).not.toBeInTheDocument();
  });

  it("labels nothing for a source cited without a quotation", () => {
    const [named] = claimRefs(
      { supporting_source_ids: ["narrative-1"] },
      parseCaseSources([narrative], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    render(<SourceDrawer sourceRef={named} anchorElement={anchor} onClose={vi.fn()} />);

    expect(screen.queryAllByRole("heading", { level: 3 })).toEqual([]);
  });

  it("shows the quotation alone when the analysis stored no context for it", () => {
    const quoted = openCited({
      source_id: "narrative-1",
      exact_quote: "a transfer of 52,000 baht",
    });

    expect(quoted).toHaveTextContent(/^a transfer of 52,000 baht$/);
    expect(quoted.querySelector("strong")).toBeNull();
  });
});
