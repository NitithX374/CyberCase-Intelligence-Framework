import { describe, expect, it } from "vitest";
import { validationSummary } from "@/features/analysis/validationSummary";
import { claim, trace } from "@/test/fixtures";
import { sourceMetrics } from "@/test/features/analysis/validationFixtures";

describe("saved analysis validation counts", () => {
  it("counts semantic admission independently of source binding", () => {
    const result = validationSummary(
      trace({
        involved_parties: [
          {
            name: "John",
            role: "Attacker",
            support: "bound",
            projection_grounding: {
              verdict: "not_supported",
              reason: "neutral",
            },
          },
          {
            name: "Jane",
            role: "Victim",
            support: "bound",
            projection_grounding: {
              verdict: "supported",
              reason: "entailment",
            },
          },
        ],
        timeline: [
          {
            time: "13:00",
            event: "An email arrived",
            projection_grounding: {
              verdict: "unassessed",
              reason: "model_unavailable:weights_missing",
            },
          },
        ],
        impacts: [{ description: "A historic description", support: "bound" }],
      }),
    );
    expect(result.counts).toEqual({
      supported: 1,
      not_supported: 1,
      unassessed: 1,
      not_recorded: 1,
    });
    expect(result.admitted).toBe(1);
    expect(result.withheld).toBe(2);
    expect(result.total).toBe(4);
    expect(result.reasons[0]).toMatchObject({
      count: 1,
      reason: "model_unavailable:weights_missing",
    });
  });

  it("keeps direct, recovered, legacy and unresolved claims distinguishable", () => {
    const result = validationSummary(
      trace({
        claims: [
          claim("Direct and recovered", "S1", {
            supporting_citations: [
              { source_id: "S1", exact_quote: "Direct", pointer_state: "direct" },
              { source_id: "S2", exact_quote: "Recovered", pointer_state: "recovered" },
            ],
          }),
          claim("Old source citation"),
          claim("Unresolved", "S1", { supporting_citations: [] }),
        ],
      }),
    );
    expect(result.claims).toEqual({ direct: 1, recovered: 1, legacy: 1, unresolved: 1 });
  });

  it("does not fabricate metrics or semantic checks for older traces", () => {
    const result = validationSummary(
      trace({ involved_parties: [{ name: "John", role: "Witness" }] }),
    );
    expect(result.sourceUnits).toBeNull();
    expect(result.admitted).toBe(0);
    expect(result.withheld).toBe(0);
    expect(result.counts.not_recorded).toBe(1);
  });

  it("uses the recorded structural ID counts without treating them as semantic support", () => {
    const result = validationSummary(trace({ grounding: sourceMetrics }));
    expect(result.sourceUnits).toEqual({ claimed: 4, resolved: 3, invalid: 1, rate: 0.75 });
    expect(result.admitted).toBe(0);
  });

  it("groups repeated unavailable and length-limit reasons without conflating them", () => {
    const result = validationSummary(
      trace({
        impacts: [
          {
            description: "A",
            projection_grounding: { verdict: "unassessed", reason: "context_limit" },
          },
          {
            description: "B",
            projection_grounding: { verdict: "unassessed", reason: "context_limit" },
          },
          {
            description: "C",
            projection_grounding: {
              verdict: "unassessed",
              reason: "model_unavailable:weights_missing",
            },
          },
        ],
      }),
    );
    expect(result.reasons.map(({ reason, count }) => ({ reason, count }))).toEqual([
      { reason: "context_limit", count: 2 },
      { reason: "model_unavailable:weights_missing", count: 1 },
    ]);
  });
});
