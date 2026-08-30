import { describe, expect, it } from "vitest";

import type { PersistedChatMessage } from "@/lib/api";
import { mitreCandidatesForMessage } from "@/lib/mitre-candidate";

function message(metadataOverrides: Record<string, unknown> = {}): PersistedChatMessage {
  return {
    id: "message-1",
    thread_id: "thread-1",
    ordinal: 2,
    role: "assistant",
    content: "Grounded analysis.",
    retrieval_context_id: "retrieval-1",
    created_at: "2026-08-20T00:00:00Z",
    metadata_json: {
      mitre_table: [
        {
          technique_id: "T1078",
          name: "Valid Accounts",
          entity_type: "Technique",
          score: 0.98,
        },
      ],
      analysis_trace: {
        version: "analysis_trace_v2",
        analysis_mode: "case_overview",
        retrieval_context_id: "retrieval-1",
        evidence_sha256: "a".repeat(64),
        validation_status: "validated",
        claims: [
          {
            claim_id: "A-01",
            claim_type: "reported",
            text: "Administrative credentials were reported compromised.",
            epistemic_status: "reported",
            source_message_ids: ["message-user-1"],
          },
        ],
        mitre_associations: [
          {
            association_id: "MA-01",
            technique_id: "T1078",
            claim_ids: ["A-01"],
            reason: "The behavior concerns use of a valid administrative credential.",
            status: "candidate_only",
            support_role: "external_technical_context",
          },
        ],
      },
      ...metadataOverrides,
    },
  };
}

describe("mitreCandidatesForMessage", () => {
  it("projects validated candidates through linked analysis claims", () => {
    const candidates = mitreCandidatesForMessage(message());

    expect(candidates).toEqual([
      {
        associationId: "MA-01",
        techniqueId: "T1078",
        techniqueName: "Valid Accounts",
        claims: [
          {
            claimId: "A-01",
            text: "Administrative credentials were reported compromised.",
            claimType: "reported",
            epistemicStatus: "reported",
          },
        ],
        reason: "The behavior concerns use of a valid administrative credential.",
      },
    ]);
  });

  it("rejects candidates outside the exact persisted MITRE table", () => {
    expect(
      mitreCandidatesForMessage(message({ mitre_table: [] })),
    ).toBeNull();
  });

  it("rejects invalid claim links and non-candidate semantics", () => {
    const baseTrace = message().metadata_json.analysis_trace as Record<
      string,
      unknown
    >;
    const association = (
      baseTrace.mitre_associations as Record<string, unknown>[]
    )[0];

    expect(
      mitreCandidatesForMessage(
        message({
          analysis_trace: {
            ...baseTrace,
            mitre_associations: [{ ...association, claim_ids: ["A-99"] }],
          },
        }),
      ),
    ).toBeNull();
    expect(
      mitreCandidatesForMessage(
        message({
          analysis_trace: {
            ...baseTrace,
            mitre_associations: [{ ...association, status: "confirmed" }],
          },
        }),
      ),
    ).toBeNull();
  });

  it("ignores messages without a validated v2 trace", () => {
    expect(mitreCandidatesForMessage(message({ analysis_trace: undefined }))).toBeNull();
  });
});
