import { describe, expect, it } from "vitest";
import type { CaseRead } from "@/lib/api/types";
import { caseStatusLabel } from "./caseDisplay";

function caseRecord(analysisFreshness: CaseRead["analysis_freshness"]): CaseRead {
  return {
    id: "case-1",
    title: "Payment Review",
    source_revision: 1,
    analysis_freshness: analysisFreshness,
    created_at: "2026-09-14T08:00:00Z",
    updated_at: "2026-09-14T08:10:00Z",
  } as CaseRead;
}

describe("caseStatusLabel", () => {
  it("names the state of the case's analysis from its freshness alone", () => {
    expect(caseStatusLabel(caseRecord("missing"))).toBe("Not analyzed");
    expect(caseStatusLabel(caseRecord("current"))).toBe("Analyzed");
    expect(caseStatusLabel(caseRecord("stale"))).toBe("Out of date");
  });
});
