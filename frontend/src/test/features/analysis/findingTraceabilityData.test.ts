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
          },
        }),
      );
      expect(state.direct).toBe(1);
      expect(state.semanticSupport).toBe(verdict);
      expect(state.semanticReason).toBeDefined();
    },
  );

  it("separates direct, recovered and legacy pointers without implying semantic support", () => {
    const state = findingTraceabilityData(
      claim("John sent an email.", "S1", {
        supporting_citations: [
          direct,
          { source_id: "S2", exact_quote: "An email was sent.", pointer_state: "recovered" },
          { source_id: "S3", exact_quote: "An email." },
        ],
      }),
    );
    expect(state).toEqual({
      direct: 1,
      recovered: 1,
      legacy: 1,
      unresolved: 0,
      semanticSupport: "unassessed",
    });
  });

  it("does not inflate counts for repeated citations or a duplicate-ID diagnostic", () => {
    const state = findingTraceabilityData(
      claim("John sent an email.", "S1", {
        supporting_citations: [direct, direct],
        invalid_evidence: [
          {
            source_id: "S1",
            evidence_unit_id: "S1:U001-revision",
            role: "supporting",
            pointer_state: "unresolved",
            reason: "duplicate_id",
          },
        ],
      }),
    );
    expect(state.direct).toBe(1);
    expect(state.unresolved).toBe(0);
  });

  it("counts a bad pointer once when both invalid and unverified records describe it", () => {
    const state = findingTraceabilityData(
      claim("A reported transfer.", "S1", {
        supporting_citations: [],
        invalid_evidence: [
          {
            source_id: "S1",
            evidence_unit_id: "S1:U001-old",
            role: "supporting",
            pointer_state: "unresolved",
            reason: "stale_id",
          },
        ],
        unverified_citations: [
          {
            source_id: "S1",
            evidence_unit_id: "S1:U001-old",
            role: "supporting",
            written_quote: "",
          },
        ],
      }),
    );
    expect(state.unresolved).toBe(1);
  });

  it("keeps NLI meaning pointers unresolved and excludes conflicting pointers from supporting counts", () => {
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
    expect(state).toEqual({
      direct: 0,
      recovered: 0,
      legacy: 0,
      unresolved: 1,
      semanticSupport: "unassessed",
    });
  });
});
