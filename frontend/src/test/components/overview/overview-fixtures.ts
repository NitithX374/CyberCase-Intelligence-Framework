import type { PersistedChatMessage } from "@/lib/api";

export function sourceMessage(id: string, ordinal: number, content: string): PersistedChatMessage {
  return {
    id,
    thread_id: "thread-1",
    ordinal,
    role: "user",
    content,
    retrieval_context_id: null,
    metadata_json: {
      evidence_kind: ordinal === 1 ? "initial_case_narrative" : "clarification_answer",
    },
    created_at: `2026-08-23T10:0${ordinal}:00Z`,
  };
}

export function analysisMessage(cyber = true): PersistedChatMessage {
  return {
    id: "analysis-1",
    thread_id: "thread-1",
    ordinal: 3,
    role: "assistant",
    content: "Rendered narrative is separate from the structured trace.",
    retrieval_context_id: cyber ? "context-1" : null,
    metadata_json: {
      analysis_kind: "grounded_main_analysis",
      analysis_state_scope: "canonical_case_overview",
      analysis_trace: {
        version: "analysis_trace_v3",
        validation_status: "validated",
        analysis_mode: "case_overview",
        summary: "The case material contains conflicting recipient information.",
        claims: [
          {
            claim_id: "A-01",
            claim_type: "reported",
            text: "The reporting party named Account A.",
            epistemic_status: "contradicted",
            supporting_source_message_ids: ["source-1"],
            contradicting_source_message_ids: ["source-2"],
            reasoning_summary: null,
          },
          {
            claim_id: "A-02",
            claim_type: "analytical_inference",
            text: "The recipient identity is not established.",
            epistemic_status: "not_established",
            supporting_source_message_ids: ["source-1", "source-2"],
            contradicting_source_message_ids: [],
            reasoning_summary: "The submitted sources identify different accounts.",
          },
        ],
        gaps: [
          {
            gap_id: "G-01",
            topic: "Recipient identity",
            status: "CONFLICTING",
            description: "Current sources name different recipient accounts.",
            affected_claim_ids: ["A-01", "A-02"],
            reason: "No current source resolves the discrepancy.",
            priority: "high",
            askable: true,
          },
        ],
        mitre_associations: cyber
          ? [{
              association_id: "MA-01",
              technique_id: "T1566.002",
              claim_ids: ["A-02"],
              reason: "The submitted material mentions a suspicious link.",
              status: "candidate_only",
              support_role: "external_technical_context",
            }]
          : [],
        evidence_sha256: "b".repeat(64),
        retrieval_context_id: cyber ? "context-1" : null,
      },
      mitre_applicability: { decision: cyber ? "RETRIEVE" : "SKIP" },
      rag_attempt: { status: cyber ? "used" : "no_applicable_context" },
      mitre_table: cyber
        ? [{
            technique_id: "T1566.002",
            name: "Spearphishing Link",
            description: "A link may be used to gain access.",
          }]
        : [],
    },
    created_at: "2026-08-23T10:03:00Z",
  };
}
