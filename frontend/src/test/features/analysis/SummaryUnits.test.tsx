import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SummaryUnits } from "@/features/analysis/SummaryUnits";
import type { SummaryUnit } from "@/features/analysis/types";

const caseId = "22222222-2222-4222-8222-222222222222";
const findings = `/case/${caseId}/analysis/findings`;

function unit(overrides: Partial<SummaryUnit> & Pick<SummaryUnit, "text">): SummaryUnit {
  return {
    claimIds: [],
    marks: [],
    closing: "",
    supportNote: null,
    noteMark: null,
    ...overrides,
  };
}

const units: SummaryUnit[] = [
  unit({
    text: "A share was encrypted",
    claimIds: ["A-01"],
    marks: [{ number: 1, claimId: "A-01" }],
    closing: ".",
  }),
  unit({
    text: "Both demands were made",
    claimIds: ["A-03", "A-07"],
    marks: [
      { number: 3, claimId: "A-03" },
      { number: 12, claimId: "A-07" },
    ],
    closing: ",",
    supportNote: "Some cited quotations were not found in the sources.",
    noteMark: "a",
  }),
  unit({
    text: "but someone is to blame",
    closing: ".",
    supportNote: "Not linked to any claim.",
    noteMark: "b",
  }),
];

describe("Summary units", () => {
  it("reads as one paragraph, the sentences in order, each followed by its raised numbers", () => {
    render(<SummaryUnits caseId={caseId} units={units} thai={false} />);

    const paragraphs = screen.getAllByRole("paragraph");
    expect(paragraphs).toHaveLength(1);
    expect(paragraphs[0]).toHaveTextContent(
      "A share was encrypted1. Both demands were made3,12a, but someone is to blameb.",
    );
    expect(paragraphs[0].querySelectorAll("sup")).toHaveLength(4);
  });

  it("makes each number a link to its finding, with a name a screen reader can say", () => {
    render(<SummaryUnits caseId={caseId} units={units} thai={false} />);

    const links = screen.getAllByRole("link");
    expect(links.map((link) => [link.textContent, link.getAttribute("aria-label")])).toEqual([
      ["1", "Finding 1"],
      ["3", "Finding 3"],
      ["12", "Finding 12"],
    ]);
    expect(links.map((link) => link.getAttribute("href"))).toEqual([
      `${findings}?finding=A-01`,
      `${findings}?finding=A-03`,
      `${findings}?finding=A-07`,
    ]);
    expect(screen.getByRole("link", { name: "Finding 12" })).toHaveTextContent("12");
  });

  it("can be reached with the keyboard", () => {
    render(<SummaryUnits caseId={caseId} units={units} thai={false} />);

    const link = screen.getByRole("link", { name: "Finding 3" });
    link.focus();

    expect(link).toHaveFocus();
    expect(link).toHaveAttribute("href");
    expect(link).not.toHaveAttribute("tabindex", "-1");
  });

  it("names the numbers in Thai when the summary is in Thai", () => {
    render(<SummaryUnits caseId={caseId} units={units} thai />);

    expect(screen.getByRole("link", { name: "ข้อ 3" })).toBeInTheDocument();
    expect(screen.getByText("ตัวเลขยกคือเลขข้อค้นพบ กดเพื่อเปิดข้อนั้น")).toBeInTheDocument();
  });

  it("says once, under the paragraph, what the raised numbers are", () => {
    render(<SummaryUnits caseId={caseId} units={units} thai={false} />);

    expect(
      screen.getAllByText("Raised numbers are finding numbers; each opens its finding."),
    ).toHaveLength(1);
  });

  it("prints each note once under the paragraph, tied to its unit by its letter", () => {
    const { container } = render(<SummaryUnits caseId={caseId} units={units} thai={false} />);

    const notes = Array.from(container.querySelectorAll("div")).map((note) => note.textContent);
    expect(notes).toEqual([
      "Raised numbers are finding numbers; each opens its finding.",
      "a Some cited quotations were not found in the sources.",
      "b Not linked to any claim.",
    ]);
    expect(screen.getAllByText("Not linked to any claim.", { exact: false })).toHaveLength(1);
  });

  it("gives a unit whose claims are all checked no letter and no note", () => {
    render(<SummaryUnits caseId={caseId} units={[units[0]]} thai={false} />);

    expect(screen.getByRole("paragraph")).toHaveTextContent("A share was encrypted1.");
    expect(screen.getByRole("paragraph").querySelectorAll("sup")).toHaveLength(1);
    expect(screen.queryByText(/not found|Not linked/)).not.toBeInTheDocument();
  });

  it("says nothing about numbers when no sentence names a finding", () => {
    render(<SummaryUnits caseId={caseId} units={[units[2]]} thai={false} />);

    expect(screen.queryByText(/Raised numbers/)).not.toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(within(screen.getByRole("paragraph")).getByText("b")).toBeInTheDocument();
  });

  it("keeps the text of a sentence as a text node, never as markup", () => {
    const hostile = unit({ text: "<b>bold</b> & <script>x</script>", closing: "." });

    const { container } = render(<SummaryUnits caseId={caseId} units={[hostile]} thai={false} />);

    expect(container.querySelector("b, script")).toBeNull();
    expect(screen.getByRole("paragraph")).toHaveTextContent("<b>bold</b> & <script>x</script>.");
  });

  it("holds a long Thai summary in one paragraph", () => {
    const many = Array.from({ length: 40 }, (_, index) =>
      unit({
        text: `ผู้เสียหายรายที่ ${index + 1} โอนเงินไปยังบัญชีของคนร้าย`,
        claimIds: [`A-${String(index + 1).padStart(2, "0")}`],
        marks: [{ number: index + 1, claimId: `A-${String(index + 1).padStart(2, "0")}` }],
      }),
    );

    render(<SummaryUnits caseId={caseId} units={many} thai />);

    expect(screen.getAllByRole("paragraph")).toHaveLength(1);
    expect(screen.getAllByRole("link")).toHaveLength(40);
  });

  it("draws no badge, pill or icon", () => {
    const { container } = render(<SummaryUnits caseId={caseId} units={units} thai={false} />);

    expect(container.querySelector("svg, img, button")).toBeNull();
    expect(container.innerHTML).not.toMatch(/rounded|bg-/);
  });
});
