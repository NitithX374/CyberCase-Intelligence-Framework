import { describe, expect, it } from "vitest";
import { groupSourceRefs } from "@/features/citations/groupSourceRefs";
import type { SourceMessageRef } from "@/features/citations/types";

function source(overrides: Partial<SourceMessageRef> = {}): SourceMessageRef {
  return {
    id: "S1",
    label: "report.pdf · p. 1",
    displayContent: "John sent an email.",
    exactQuote: "John sent an email.",
    quoteContext: null,
    filename: "report.pdf",
    pageNumbers: [1],
    sourcePages: [{ pageNumber: 1, text: "John sent an email." }],
    question: null,
    pointerState: "direct",
    start: 0,
    end: 19,
    ...overrides,
  };
}

describe("Grouped Finding Source passages", () => {
  it("preserves all distinct spans on one page in source-selection order without mutating input", () => {
    const refs = [source(), source({ exactQuote: "It arrived Monday.", start: 20, end: 38 })];
    const snapshot = structuredClone(refs);
    const groups = groupSourceRefs(refs);
    expect(groups).toHaveLength(1);
    expect(groups[0].passages?.map((item) => item.quote)).toEqual([
      "John sent an email.",
      "It arrived Monday.",
    ]);
    expect(refs).toEqual(snapshot);
  });

  it("preserves separate occurrences of identical text at different offsets", () => {
    const groups = groupSourceRefs([source(), source({ start: 40, end: 59 })]);
    expect(groups[0].passages).toHaveLength(2);
    expect(groups[0].passages?.map((item) => item.start)).toEqual([0, 40]);
  });

  it("deduplicates the same span while retaining its review notes", () => {
    const groups = groupSourceRefs([
      source({ reviewNotes: ["Review the amount."] }),
      source({ toleratedNotes: ["Formatting differs."] }),
    ]);
    expect(groups[0].passages).toHaveLength(1);
    expect(groups[0].passages?.[0].notes).toEqual(["Review the amount.", "Formatting differs."]);
  });

  it("never merges different Sources or pages, even with identical filenames and text", () => {
    const groups = groupSourceRefs([
      source(),
      source({ id: "S2" }),
      source({ label: "report.pdf · p. 2", pageNumbers: [2] }),
    ]);
    expect(groups).toHaveLength(3);
    expect(groups.map((item) => item.id)).toEqual(["S1", "S2", "S1"]);
  });
});
