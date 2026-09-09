import { expect, it } from "vitest";
import { buildCaseOverview } from "@/lib/case-overview";
import type { PersistedChatMessage } from "@/lib/api";

function record(ordinal: number, metadata: Record<string, unknown>): PersistedChatMessage {
  return { id: String(ordinal), thread_id: "thread", ordinal, role: "assistant",
    content: "Analysis", retrieval_context_id: null, metadata_json: metadata,
    created_at: "2026-09-09T00:00:00Z" };
}
const old = record(1, { analysis_trace: {
  version: "analysis_trace_v3", validation_status: "validated",
  analysis_mode: "case_overview", summary: "Old summary", claims: [], gaps: [],
  mitre_associations: [],
} });

it.each(["analysis_trace_v2", "analysis_trace_v3", "analysis_trace_v9"])(
  "does not fall back to older v3 for a newer %s record", (version) => {
    const latest = record(3, { analysis_kind: "grounded_main_analysis",
      analysis_trace: { version, analysis_mode: "case_overview", validation_status: "unavailable" } });
    const result = buildCaseOverview([latest, old]);
    expect(result.analysisMessageId).toBe("3");
    expect(result.findings).toEqual([]);
    expect(result.incidentSummary.includes("earlier schema")).toBe(version === "analysis_trace_v2");
  });

it("identifies a failed current analysis without calling it legacy", () => {
  const latest = record(3, { analysis_state_scope: "canonical_case_overview",
    analysis_trace_failure: { version: "analysis_trace_v3" } });
  const result = buildCaseOverview([old, latest]);
  expect(result.analysisMessageId).toBe("3");
  expect(result.incidentSummary).toContain("unavailable");
});

it.each([
  { analysis_state_scope: "response_scoped" }, { canonical_case_state: false },
  { chat_action: { action: "ask" } },
])("ignores response-scoped legacy markers %o", (scope) => {
  const latest = record(3, { analysis_kind: "grounded_main_analysis",
    analysis_trace: { version: "analysis_trace_v2" }, ...scope });
  expect(buildCaseOverview([old, latest]).analysisMessageId).toBe("1");
});
