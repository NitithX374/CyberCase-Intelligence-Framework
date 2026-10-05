import { describe, expect, it } from "vitest";
import { buildCaseOverview, findingNumbers } from "@/features/analysis/overview";
import { analysisResult, claim, narrativeSource, trace } from "@/test/fixtures";

const quote = "A file share was encrypted overnight.";
const sourceId = narrativeSource(quote).id;

function claimWith(id: string, text: string) {
  return claim(text, sourceId, { claim_id: id, text });
}

const claims = [
  claimWith("A-01", "first"),
  claimWith("A-02", "second"),
  claimWith("A-03", "first"),
  claimWith("A-04", "third"),
];

describe("finding numbers", () => {
  it("numbers the claims in order, two claims with the same text sharing the first one's number", () => {
    const numbers = findingNumbers(claims);

    expect([...numbers].map(([id, mark]) => [id, mark.number, mark.claimId])).toEqual([
      ["A-01", 1, "A-01"],
      ["A-02", 2, "A-02"],
      ["A-03", 1, "A-01"],
      ["A-04", 3, "A-04"],
    ]);
  });

  it("ignores the whitespace around a claim's text, as the report does", () => {
    const numbers = findingNumbers([claimWith("A-01", " same "), claimWith("A-02", "same")]);

    expect(numbers.get("A-02")?.number).toBe(1);
  });
});

describe("summary marks", () => {
  const summary = "Alpha [A-03]. Beta [A-04, A-01]. Gamma [A-02]. Delta.";
  const result = analysisResult({
    summary,
    trace_json: trace({
      summary,
      claims,
      summary_units: [
        { text: "Alpha", claim_ids: ["A-03"], support: "bound" },
        { text: "Beta", claim_ids: ["A-04", "A-01"], support: "bound" },
        { text: "Gamma", claim_ids: ["A-02"], support: "bound" },
        { text: "Delta.", claim_ids: [], support: "no_claim" },
      ],
    }),
  });

  it("gives each sentence the numbers of its findings, once each and in order", () => {
    const { summaryUnits } = buildCaseOverview(result, [narrativeSource(quote)]);

    expect(summaryUnits.map((unit) => unit.marks.map((mark) => mark.number))).toEqual([
      [1],
      [1, 3],
      [2],
      [],
    ]);
    expect(summaryUnits[0].marks[0].claimId).toBe("A-01");
  });

  it("matches the numbers the report prints for the same claims and units", () => {
    const { summaryUnits } = buildCaseOverview(result, [narrativeSource(quote)]);

    expect(summaryUnits.map((unit) => unit.marks.map((mark) => mark.number))).toEqual([
      [1],
      [1, 3],
      [2],
      [],
    ]);
  });

  it("restores the punctuation the summary had after each bracket", () => {
    const { summaryUnits } = buildCaseOverview(result, [narrativeSource(quote)]);

    expect(summaryUnits.map((unit) => unit.closing)).toEqual([".", ".", ".", ""]);
  });

  it("prints no punctuation when the summary no longer matches its units", () => {
    const stale = analysisResult({
      summary: "Alpha [A-03]. Beta [A-04].",
      trace_json: trace({
        summary: "Alpha [A-03]. Beta [A-04].",
        claims,
        summary_units: [{ text: "Alpha", claim_ids: ["A-03"], support: "bound" }],
      }),
    });

    const { summaryUnits } = buildCaseOverview(stale, [narrativeSource(quote)]);

    expect(summaryUnits.map((unit) => unit.closing)).toEqual([""]);
  });

  it("gives a note letter to each unit that needs a note, in order, past z", () => {
    const many = Array.from({ length: 28 }, (_, index) => ({
      text: `Unit ${index}`,
      claim_ids: [],
      support: "no_claim" as const,
    }));
    const long = analysisResult({
      summary: "x",
      trace_json: trace({ summary: "x", claims, summary_units: many }),
    });

    const { summaryUnits } = buildCaseOverview(long, [narrativeSource(quote)]);

    expect(summaryUnits[0].noteMark).toBe("a");
    expect(summaryUnits[25].noteMark).toBe("z");
    expect(summaryUnits[26].noteMark).toBe("aa");
    expect(summaryUnits[27].noteMark).toBe("ab");
  });
});
