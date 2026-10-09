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
            model: "test-nli",
            entailment: verdict === "unassessed" ? null : verdict === "supported" ? 0.99 : 0.1,
            threshold: 0.8,
            duration_ms: 0,
            selection_ms: 0,
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

  it("does not imply semantic support from NLI meaning pointers", () => {
    const state = findingTraceabilityData(
      claim("A reported transfer.", "S1", {
        supporting_citations: [],
        contradicting_citations: [direct],
        unverified_citations: [
          {
            source_id: "S1",
            role: "supporting",
            written_quote: "Not found.",
            meaning_passage: {
              source_text: "A related transfer.",
              start: 0,
              end: 19,
              entailment: 0.99,
              model: "test-nli",
            },
          },
          { source_id: "S2", role: "contradicting", written_quote: "A conflict." },
        ],
      }),
    );
    expect(state).toEqual({ semanticSupport: "unassessed" });
  });
});
