import { render, screen } from "@testing-library/react";
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

    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent(/^Source: Your answer 1$/);
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

    expect(labels).toEqual(["statement.pdf", "Narrative 1", "Narrative 2"]);
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
  }

  it("shows the whole source with the quotation marked once, in place", () => {
    openCited({
      source_id: "narrative-1",
      exact_quote: "a transfer of 52,000 baht",
      pointer_state: "recovered",
      context: {
        before: "The caller said the account had been frozen. He asked for ",
        after: " to a safe account.",
        cut_before: false,
        cut_after: false,
      },
    });

    expect(screen.getByLabelText("Source text")).toHaveTextContent(narrative.exact_text);
    expect(Array.from(document.querySelectorAll("mark"), (mark) => mark.textContent)).toEqual([
      "a transfer of 52,000 baht",
    ]);
    expect(screen.queryByRole("heading", { level: 3 })).not.toBeInTheDocument();
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

  it("marks the quotation where its offsets point, not at an earlier repeat of the words", () => {
    const repeated = {
      ...caseSource("narrative-2", "narrative"),
      exact_text: "He asked for 500 baht. Later he asked for 500 baht again.",
    };
    const start = repeated.exact_text.lastIndexOf("500 baht");
    const [cited] = claimRefs(
      {
        supporting_source_ids: ["narrative-2"],
        supporting_citations: [
          {
            source_id: "narrative-2",
            exact_quote: "500 baht",
            pointer_state: "direct",
            start,
            end: start + "500 baht".length,
          },
        ],
      },
      parseCaseSources([repeated], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));
    render(<SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />);

    const marks = document.querySelectorAll("mark");
    expect(marks).toHaveLength(1);
    expect(marks[0].previousSibling?.textContent).toBe(
      "He asked for 500 baht. Later he asked for ",
    );
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

    const { baseElement: container } = render(
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
            pointer_state: "recovered",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    const { baseElement: container } = render(
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
            pointer_state: "recovered",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    const { baseElement: container } = render(
      <SourceDrawer sourceRef={cited} anchorElement={anchor} onClose={vi.fn()} />,
    );

    const tdMarks = container.querySelectorAll("td mark");
    expect(tdMarks).toHaveLength(2);
    expect(tdMarks[0]).toHaveTextContent("นายถนอม รอดสุข");
    expect(tdMarks[1]).toHaveTextContent("ผู้กล่าวหา");
    const tr = container.querySelector("tr");
    expect(tr?.className).toContain("bg-primary-wash");
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
            pointer_state: "recovered",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor = document.body.appendChild(document.createElement("button"));

    const { baseElement: container } = render(
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
            pointer_state: "recovered",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor1 = document.body.appendChild(document.createElement("button"));

    const first = render(
      <SourceDrawer sourceRef={citedLeading} anchorElement={anchor1} onClose={vi.fn()} />,
    );
    expect(document.body.querySelector("td mark")).toHaveTextContent("นายถนอม รอดสุข");
    expect(document.body.querySelector("table")).not.toBeNull();
    first.unmount();

    const [citedTrailing] = claimRefs(
      {
        supporting_source_ids: ["doc-5"],
        supporting_citations: [
          {
            source_id: "doc-5",
            exact_quote: "<tr><td>นางสาวสุรัตนา</td></tr></table>",
            pointer_state: "recovered",
            page_numbers: [1],
          },
        ],
      },
      parseCaseSources([docSource], []),
    ).supporting;
    const anchor2 = document.body.appendChild(document.createElement("button"));

    render(<SourceDrawer sourceRef={citedTrailing} anchorElement={anchor2} onClose={vi.fn()} />);
    expect(document.body.querySelector("td mark")).toHaveTextContent("นางสาวสุรัตนา");
    expect(document.body.querySelector("table")).not.toBeNull();
  });
});
