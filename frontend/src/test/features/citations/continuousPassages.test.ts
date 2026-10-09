import { describe, expect, it } from "vitest";
import { continuousPassages } from "@/features/citations/continuousPassages";
import type { CitedSourcePassage, SourceMessageRef } from "@/features/citations/types";

function passage(quote: string, start: number, pointerState: "direct" | "recovered" = "direct") {
  return {
    quote,
    start,
    end: start + Array.from(quote).length,
    pointerState,
    context: null,
    notes: [],
  } satisfies CitedSourcePassage;
}

function source(passages: CitedSourcePassage[]): SourceMessageRef {
  return {
    id: "S1",
    label: "report.pdf",
    displayContent: "",
    exactQuote: null,
    quoteContext: null,
    filename: "report.pdf",
    pageNumbers: [2],
    sourcePages: [],
    question: null,
    passages,
  };
}

describe("Continuous Source passages", () => {
  it("joins adjacent fragments in source order without duplicating context or mutating citations", () => {
    const first = {
      ...passage("Jane ", 0),
      context: { before: "Intro\n", after: "", cutBefore: false, cutAfter: false },
    };
    const second = {
      ...passage("aged 43 | Complainant", 5),
      context: { before: "Jane ", after: "\nEnd", cutBefore: false, cutAfter: false },
    };
    const input = source([second, first]);
    const snapshot = structuredClone(input);
    const [merged] = continuousPassages(input);
    expect(merged.quote).toBe("Jane aged 43 | Complainant");
    expect(merged.context).toEqual({
      before: "Intro\n",
      after: "\nEnd",
      cutBefore: false,
      cutAfter: false,
    });
    expect(input).toEqual(snapshot);
  });

  it("does not bridge missing text or mix direct and recovered locations", () => {
    expect(continuousPassages(source([passage("Jane", 0), passage("Victim", 20)]))).toHaveLength(2);
    expect(
      continuousPassages(source([passage("Jane", 0), passage("Victim", 4, "recovered")])),
    ).toHaveLength(2);
  });

  it("uses original Unicode code-point offsets", () => {
    expect(
      continuousPassages(source([passage("😀 Jane ", 0), passage("Victim", 7)]))[0].quote,
    ).toBe("😀 Jane Victim");
  });
});
