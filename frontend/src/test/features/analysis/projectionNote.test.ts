import { describe, expect, it } from "vitest";
import { projectionNote } from "@/features/analysis/projectionNote";
import { buildCaseOverview } from "@/features/analysis/overview";
import { analysisResult, claim, narrativeSource, sourceId, trace } from "@/test/fixtures";

describe("Projection support", () => {
  it("does not equate bound evidence with support for an attacker role", () => {
    const result = analysisResult({
      trace_json: trace({
        claims: [claim("John sent an email.", sourceId)],
        involved_parties: [
          {
            name: "John",
            role: "Attacker",
            claim_ids: ["A-01"],
            support: "bound",
            projection_grounding: { verdict: "not_supported", reason: "neutral" },
          },
        ],
      }),
    });
    const [party] = buildCaseOverview(result, [narrativeSource("John sent an email.")]).parties;
    expect(party.supportNote).toBe("The linked findings do not support this description.");
  });

  it("keeps binding and semantic warnings distinct", () => {
    expect(
      projectionNote(
        "unbound",
        { verdict: "unassessed", reason: "unbound_claim" },
        "An incident occurred.",
      ),
    ).toBe(
      "No cited quotation was found in the sources. Support for this description has not been assessed.",
    );
  });

  it("does not label an unavailable verifier as confirmation", () => {
    expect(
      projectionNote(
        "bound",
        { verdict: "unassessed", reason: "model_unavailable:weights_missing" },
        "An incident occurred.",
      ),
    ).toBe("Support for this description has not been assessed.");
  });

  it("uses Thai when the analysis is Thai", () => {
    expect(
      projectionNote("bound", { verdict: "not_supported", reason: "neutral" }, "มีการแจ้งเหตุ"),
    ).toBe("ข้อสังเกตที่เชื่อมไว้ไม่สนับสนุนข้อมูลนี้");
  });

  it("preserves older traces without inventing a semantic verdict", () => {
    expect(projectionNote("bound", null, "An incident occurred.")).toBeNull();
    expect(
      projectionNote(
        "bound",
        { verdict: "supported", reason: "entailment" },
        "An incident occurred.",
      ),
    ).toBeNull();
  });
});
