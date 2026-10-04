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

  it("says under the quotation what the locator ignored to find it", () => {
    const [cited] = claimRefs(
      {
        supporting_source_ids: ["narrative-1"],
        supporting_citations: [
          {
            source_id: "narrative-1",
            exact_quote: "a transfer of 52,000 baht",
            tolerated_differences: [
              { written: "apple", source: "Apple" },
              { written: "", source: "-" },
            ],
          },
        ],
      },
      parseCaseSources([narrative], []),
      "A transfer was reported.",
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    render(<SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />);

    const quoted = screen.getByRole("heading", { level: 3, name: "Quoted" }).closest("section")!;
    expect(
      within(quoted).getByText(
        "Found in the source when formatting is ignored. The analysis wrote «apple»; the source says «Apple».",
      ),
    ).toBeInTheDocument();
    expect(
      within(quoted).getByText(
        "Found in the source when formatting is ignored. The source has «-», which the analysis leaves out.",
      ),
    ).toBeInTheDocument();
  });

  it("shows no line for a quotation found as written, or when the caller gave no text", () => {
    const withDifference = {
      source_id: "narrative-1",
      exact_quote: "a transfer of 52,000 baht",
      tolerated_differences: [{ written: "apple", source: "Apple" }],
    };
    const sources = parseCaseSources([narrative], []);
    const [plain] = claimRefs(
      {
        supporting_source_ids: ["narrative-1"],
        supporting_citations: [{ source_id: "narrative-1", exact_quote: "a transfer" }],
      },
      sources,
      "A transfer was reported.",
    ).supporting;
    const [withoutText] = claimRefs(
      { supporting_source_ids: ["narrative-1"], supporting_citations: [withDifference] },
      sources,
    ).supporting;

    expect(plain.toleratedNotes).toBeUndefined();
    expect(withoutText.toleratedNotes).toBeUndefined();
  });

  it("tells the reader under the quotation which mark to check", () => {
    const [cited] = claimRefs(
      {
        supporting_source_ids: ["narrative-1"],
        supporting_citations: [
          {
            source_id: "narrative-1",
            exact_quote: "a transfer of 52,000 baht",
            tolerated_differences: [{ written: "apple", source: "Apple" }],
            review_flags: [
              { kind: "meaning_mark", verdict: "rule_warning", detail: "? edge" },
              { kind: "meaning_mark", verdict: "rule_warning", detail: "~ ignored" },
            ],
          },
        ],
      },
      parseCaseSources([narrative], []),
      "A transfer was reported.",
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    render(<SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />);

    const quoted = screen.getByRole("heading", { level: 3, name: "Quoted" }).closest("section")!;
    const lines = within(quoted)
      .getAllByText(/^(Found in the source|Check:)/)
      .map((line) => line.textContent);
    expect(lines).toEqual([
      "Found in the source when formatting is ignored. The analysis wrote «apple»; the source says «Apple».",
      "Check: the source has the mark ? next to the quote, which the quote leaves out.",
      "Check: the quote and the source differ at the mark ~, which may change the meaning.",
    ]);
    expect(quoted.querySelector("svg, img, button")).toBeNull();
  });

  it("shows no mark line for a quotation with no flag, or without the analysis text", () => {
    const citation: CaseSourceCitation = {
      source_id: "narrative-1",
      exact_quote: "a transfer of 52,000 baht",
      review_flags: [{ kind: "meaning_mark", verdict: "rule_warning", detail: "? edge" }],
    };
    const sources = parseCaseSources([narrative], []);
    const [plain] = claimRefs(
      {
        supporting_source_ids: ["narrative-1"],
        supporting_citations: [{ source_id: "narrative-1", exact_quote: "a transfer" }],
      },
      sources,
      "A transfer was reported.",
    ).supporting;
    const [withoutText] = claimRefs(
      { supporting_source_ids: ["narrative-1"], supporting_citations: [citation] },
      sources,
    ).supporting;

    expect(plain.reviewNotes).toBeUndefined();
    expect(withoutText.reviewNotes).toBeUndefined();
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
