import { describe, expect, it } from "vitest";
import type { CaseSourceCitation } from "@/lib/api/types";
import { findingTraceabilityData } from "@/features/analysis/findingTraceabilityData";
import { claim } from "@/test/fixtures";

const direct: CaseSourceCitation = {
  source_id: "S1",
  exact_quote: "John sent an email.",
  pointer_state: "direct",
  evidence_unit_ids: ["S1:U001-revision"],
  start: 0,
  end: 19,
};

describe("Saved Finding Source linkage", () => {
  it.each(["supported", "not_supported", "unassessed"] as const)(
    "reads the saved Claim verdict %s instead of inferring it from resolved citations",
    (verdict) => {
      const state = findingTraceabilityData(
        claim("John sent an email.", "S1", {
          supporting_citations: [direct],
          semantic_grounding: {
            verdict,
            reason:
              verdict === "supported"
                ? "entailed"
                : verdict === "not_supported"
                  ? "neutral"
                  : "input_too_long",
          },
        }),
      );
      expect(state.semanticSupport).toBe(verdict);
      expect(state.semanticReason).toBeDefined();
    },
  );

  it("does not imply semantic support from direct, recovered and legacy pointers", () => {
    const state = findingTraceabilityData(
      claim("John sent an email.", "S1", {
        supporting_citations: [
          direct,
          { source_id: "S2", exact_quote: "An email was sent.", pointer_state: "recovered" },
          { source_id: "S3", exact_quote: "An email." },
        ],
      }),
    );
    expect(state).toEqual({ semanticSupport: "unassessed" });
  });

  it("does not imply semantic support from unresolved citations", () => {
    const state = findingTraceabilityData(
      claim("A reported transfer.", "S1", {
        supporting_citations: [],
        contradicting_citations: [direct],
        unverified_citations: [
          { source_id: "S1", role: "supporting", evidence_unit_id: "S1:U009-0000000000000000" },
          { source_id: "S2", role: "contradicting" },
        ],
      }),
    );
    expect(state).toEqual({ semanticSupport: "unassessed" });
  });
});
