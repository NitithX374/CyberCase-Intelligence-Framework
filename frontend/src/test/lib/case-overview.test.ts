import { describe, expect, it } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import { buildCaseOverview } from "@/lib/case-overview";

function message(
  id: string,
  ordinal: number,
  role: "user" | "assistant",
  content: string,
  metadata_json: Record<string, unknown>,
): PersistedChatMessage {
  return {
    id,
    thread_id: "thread-1",
    ordinal,
    role,
    content,
    retrieval_context_id: null,
    metadata_json,
    created_at: `2026-08-23T10:0${ordinal}:00Z`,
  };
}

function v3Trace(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    version: "analysis_trace_v3",
    validation_status: "validated",
    analysis_mode: "case_overview",
    summary: "The submitted material reports an event that remains under review.",
    claims: [],
    gaps: [],
    mitre_associations: [],
    evidence_sha256: "a".repeat(64),
    retrieval_context_id: null,
    ...overrides,
  };
}

describe("case-overview view model builder", () => {
  it("returns an empty domain model when no analysis exists", () => {
    const overview = buildCaseOverview([], "idle");
    expect(overview).toMatchObject({
      hasAnalysis: false,
      isProcessing: false,
      incidentSummary: "",
      findings: [],
      gaps: [],
      mitreContext: [],
      technicalContextStatus: "hidden",
      contractVersion: null,
    });
  });

  it("projects validated v3 summary, evidence roles, gaps, and optional MITRE context directly", () => {
    const supportingContent =
      "The reporting party stated that Account A received the transfer.";
    const supporting = message(
      "source-support",
      1,
      "user",
      supportingContent,
      {
        evidence_kind: "initial_case_narrative",
        document_sources: [{
          document_id: "DOC-1",
          filename: "statement.pdf",
          page_spans: [{
            page_number: 2,
            start_offset: 0,
            end_offset: supportingContent.length,
            text_sha256: "a".repeat(64),
          }],
        }],
      },
    );
    const conflicting = message(
      "source-conflict",
      2,
      "user",
      "The bank record identifies Account B as the recipient.",
      { evidence_kind: "clarification_answer" },
    );
    const analysis = message(
      "analysis-v3",
      3,
      "assistant",
      "### 1. This legacy markdown must not become the v3 summary",
      {
        analysis_kind: "grounded_main_analysis",
        analysis_state_scope: "canonical_case_overview",
        analysis_trace: v3Trace({
          summary: "Case-level summary from the validated trace.",
          claims: [
            {
              claim_id: "A-01",
              claim_type: "reported",
              text: "The reporting party identified Account A as the recipient.",
              epistemic_status: "contradicted",
              supporting_source_message_ids: ["source-support"],
              contradicting_source_message_ids: ["source-conflict"],
              supporting_citations: [{
                source_message_id: "source-support",
                exact_quote: "Account A received the transfer",
                document_id: "DOC-1",
                filename: "statement.pdf",
                page_numbers: [2],
              }],
              contradicting_citations: [],
              reasoning_summary: null,
            },
            {
              claim_id: "A-02",
              claim_type: "analytical_inference",
              text: "The recipient identity requires reconciliation.",
              epistemic_status: "not_established",
              supporting_source_message_ids: ["source-support", "source-conflict"],
              contradicting_source_message_ids: [],
              reasoning_summary: "The two submitted sources name different recipient accounts.",
            },
          ],
          gaps: [
            {
              gap_id: "G-01",
              topic: "Recipient identity",
              status: "CONFLICTING",
              description: "Submitted sources name different recipient accounts.",
              affected_claim_ids: ["A-01", "A-02"],
              reason: "The conflict cannot be resolved from current material.",
              priority: "high",
              askable: true,
            },
          ],
          mitre_associations: [
            {
              association_id: "MA-01",
              technique_id: "T1566.002",
              claim_ids: ["A-02"],
              reason: "A submitted message describes a suspicious link.",
              status: "candidate_only",
              support_role: "external_technical_context",
            },
          ],
        }),
        mitre_table: [
          {
            technique_id: "T1566.002",
            name: "Spearphishing Link",
            description: "A link may be used to gain access.",
          },
        ],
        mitre_applicability: { decision: "RETRIEVE" },
        rag_attempt: { status: "used" },
      },
    );

    const overview = buildCaseOverview([supporting, conflicting, analysis], "answered");
    expect(overview.contractVersion).toBe("v3");
    expect(overview.incidentSummary).toBe("Case-level summary from the validated trace.");
    expect(overview.findings).toHaveLength(2);
    expect(overview.findings[0].supportingSources[0].id).toBe("source-support");
    expect(overview.findings[0].supportingSources[0]).toMatchObject({
      label: "statement.pdf · p. 2",
      exactQuote: "Account A received the transfer",
      pageNumbers: [2],
    });
    expect(overview.findings[0].contradictingSources[0].id).toBe("source-conflict");
    expect(overview.findings[1].reasoningSummary).toContain("different recipient accounts");
    expect(overview.gaps[0]).toMatchObject({
      id: "G-01",
      status: "CONFLICTING",
      affectedClaimIds: ["A-01", "A-02"],
      askable: true,
    });
    expect(overview.technicalContextStatus).toBe("available");
    expect(overview.mitreContext[0].techniqueId).toBe("T1566.002");
  });

  it("hides MITRE context when applicability explicitly skips a non-cyber case", () => {
    const analysis = message("analysis-v3", 2, "assistant", "Rendered answer", {
      analysis_state_scope: "canonical_case_overview",
      analysis_trace: v3Trace(),
      mitre_applicability: { decision: "SKIP" },
      rag_attempt: { status: "no_applicable_context" },
      mitre_table: [],
    });
    const overview = buildCaseOverview([analysis], "answered");
    expect(overview.hasAnalysis).toBe(true);
    expect(overview.technicalContextStatus).toBe("hidden");
    expect(overview.mitreContext).toEqual([]);
  });

  it("keeps the canonical overview when a later question-answer trace exists", () => {
    const canonical = message("overview", 1, "assistant", "Overview answer", {
      analysis_state_scope: "canonical_case_overview",
      analysis_trace: v3Trace({ summary: "Canonical summary" }),
    });
    const answer = message("answer", 2, "assistant", "Question answer", {
      analysis_state_scope: "response_scoped",
      canonical_case_state: false,
      analysis_trace: v3Trace({
        analysis_mode: "question_answer",
        summary: "Response-scoped summary",
      }),
    });
    const overview = buildCaseOverview([canonical, answer], "answered");
    expect(overview.analysisMessageId).toBe("overview");
    expect(overview.incidentSummary).toBe("Canonical summary");
  });

  it("keeps markdown parsing isolated to validated legacy v2 messages", () => {
    const source = message("source", 1, "user", "A witness reported a cash transfer.", {
      evidence_kind: "initial_case_narrative",
    });
    const legacy = message(
      "legacy",
      2,
      "assistant",
      "### 1. Overall Case Picture\nA witness reported a cash transfer.\n\n### 2. Detail\nMore text.",
      {
        analysis_kind: "grounded_main_analysis",
        analysis_trace: {
          version: "analysis_trace_v2",
          validation_status: "validated",
          analysis_mode: "case_overview",
          claims: [{
            claim_id: "A-01",
            claim_type: "reported",
            text: "A witness reported a cash transfer.",
            epistemic_status: "reported",
            source_message_ids: ["source"],
          }],
          mitre_associations: [],
        },
      },
    );
    const overview = buildCaseOverview([source, legacy], "answered");
    expect(overview.contractVersion).toBe("legacy");
    expect(overview.incidentSummary).toBe("A witness reported a cash transfer.");
    expect(overview.findings[0].supportingSources[0].id).toBe("source");
  });
});
