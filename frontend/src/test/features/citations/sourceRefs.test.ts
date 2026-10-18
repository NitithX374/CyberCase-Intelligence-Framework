import { describe, expect, it } from "vitest";
import { claimRefs, parseCaseSources } from "@/features/citations/sourceRefs";
import { narrativeSource, sourceId } from "@/test/fixtures";

describe("Evidence Unit source offsets", () => {
  it("displays the selected repeated passage using Python character offsets", () => {
    const quote = "John sent an email.";
    const prefix = `FIRST ${quote}${"😀 middle ".repeat(160)}`;
    const text = `${prefix}${quote} SECOND`;
    const start = Array.from(prefix).length;
    const refs = claimRefs(
      {
        supporting_source_ids: [sourceId],
        supporting_citations: [
          {
            source_id: sourceId,
            pointer_state: "direct",
            evidence_unit_ids: [`${sourceId}:U002-test`],
            start,
            end: start + quote.length,
            exact_quote: quote,
          },
        ],
        contradicting_source_ids: [],
        contradicting_citations: [],
      },
      parseCaseSources([narrativeSource(text)], []),
    );
    expect(refs.supporting[0].displayContent).toContain("SECOND");
    expect(refs.supporting[0].displayContent).not.toContain("FIRST");
    expect(refs.supporting[0].exactQuote).toBe(quote);
  });
});
