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

  it("renders page text with Markdown and HTML tables instead of raw tags", () => {
    const docSource: CaseSourceRead = {
      ...caseSource("doc-1", "document", "ลำดับ01 ปก อก.1.pdf"),
      exact_text: "## Title\n<table><tr><td>ครั้งที่ ๑</td></tr></table>",
      provenance_json: {
        pages: [
          {
            page_number: 1,
            start_offset: 0,
            end_offset: 54,
          },
        ],
      },
    };

    const [cited] = claimRefs(
      { supporting_source_ids: ["doc-1"] },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    const { container } = render(
      <SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />,
    );

    expect(screen.getByRole("heading", { level: 2, name: /Header|Title/i })).toBeInTheDocument();
    expect(container.querySelector("table")).not.toBeNull();
    expect(container.querySelector("td")).toHaveTextContent("ครั้งที่ ๑");
  });

  it("highlights the quoted text with mark tag within the source text", () => {
    const docSource: CaseSourceRead = {
      ...caseSource("doc-2", "document", "report.pdf"),
      exact_text: "Police inspected the crime scene on Rama 9 Road.",
      provenance_json: {
        pages: [{ page_number: 1, start_offset: 0, end_offset: 49 }],
      },
    };

    const [cited] = claimRefs(
      {
        supporting_source_ids: ["doc-2"],
        supporting_citations: [
          {
            source_id: "doc-2",
            exact_quote: "crime scene",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    const { container } = render(
      <SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />,
    );

    const mark = container.querySelector("mark");
    expect(mark).not.toBeNull();
    expect(mark).toHaveTextContent("crime scene");
  });

  it("highlights the quoted text when the quote is an HTML table row", () => {
    const docSource: CaseSourceRead = {
      ...caseSource("doc-3", "document", "table.pdf"),
      exact_text: "## Summary\n<table><tr><td>นายถนอม รอดสุข</td><td>ผู้กล่าวหา</td></tr></table>",
      provenance_json: {
        pages: [{ page_number: 1, start_offset: 0, end_offset: 80 }],
      },
    };

    const [cited] = claimRefs(
      {
        supporting_source_ids: ["doc-3"],
        supporting_citations: [
          {
            source_id: "doc-3",
            exact_quote: "<tr><td>นายถนอม รอดสุข</td><td>ผู้กล่าวหา</td></tr>",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    const { container } = render(
      <SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />,
    );

    const tdMarks = container.querySelectorAll("td mark");
    expect(tdMarks).toHaveLength(2);
    expect(tdMarks[0]).toHaveTextContent("นายถนอม รอดสุข");
    expect(tdMarks[1]).toHaveTextContent("ผู้กล่าวหา");
    const tr = container.querySelector("tr");
    expect(tr?.className).toContain("bg-amber-100/50");
  });

  it("highlights table content when quote is pipe-separated text without tags", () => {
    const docSource: CaseSourceRead = {
      ...caseSource("doc-4", "document", "table2.pdf"),
      exact_text: "<table><tr><td>นายถนอม รอดสุข</td><td>ผู้กล่าวหา</td></tr></table>",
      provenance_json: {
        pages: [{ page_number: 1, start_offset: 0, end_offset: 80 }],
      },
    };

    const [cited] = claimRefs(
      {
        supporting_source_ids: ["doc-4"],
        supporting_citations: [
          {
            source_id: "doc-4",
            exact_quote: "นายถนอม รอดสุข | ผู้กล่าวหา",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    const { container } = render(
      <SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />,
    );

    const tdMarks = container.querySelectorAll("td mark");
    expect(tdMarks).toHaveLength(2);
    expect(tdMarks[0]).toHaveTextContent("นายถนอม รอดสุข");
    expect(tdMarks[1]).toHaveTextContent("ผู้กล่าวหา");
  });

  it("highlights table row when quote includes leading table tag or trailing table tag", () => {
    const docSource: CaseSourceRead = {
      ...caseSource("doc-5", "document", "table3.pdf"),
      exact_text: "<table><tr><td>นายถนอม รอดสุข</td></tr><tr><td>นางสาวสุรัตนา</td></tr></table>",
      provenance_json: {
        pages: [{ page_number: 1, start_offset: 0, end_offset: 90 }],
      },
    };

    const [citedLeading] = claimRefs(
      {
        supporting_source_ids: ["doc-5"],
        supporting_citations: [
          {
            source_id: "doc-5",
            exact_quote: "<table><tr><td>นายถนอม รอดสุข</td></tr>",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor1 = document.body.appendChild(document.createElement("button"));

    const { container: c1 } = render(
      <SourceDrawer sourceRef={citedLeading} anchorElement={anchor1} onClose={vi.fn()} />,
    );
    expect(c1.querySelector("td mark")).toHaveTextContent("นายถนอม รอดสุข");
    expect(c1.querySelector("table")).not.toBeNull();

    const [citedTrailing] = claimRefs(
      {
        supporting_source_ids: ["doc-5"],
        supporting_citations: [
          {
            source_id: "doc-5",
            exact_quote: "<tr><td>นางสาวสุรัตนา</td></tr></table>",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor2 = document.body.appendChild(document.createElement("button"));

    const { container: c2 } = render(
      <SourceDrawer sourceRef={citedTrailing} anchorElement={anchor2} onClose={vi.fn()} />,
    );
    expect(c2.querySelector("td mark")).toHaveTextContent("นางสาวสุรัตนา");
    expect(c2.querySelector("table")).not.toBeNull();
  });
});
