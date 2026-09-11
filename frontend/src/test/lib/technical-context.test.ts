import { describe, expect, it } from "vitest";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead, PersistedChatMessage } from "@/lib/api";
import { buildNativeTechnicalContext, buildTechnicalContext } from "@/lib/technicalContext";
import { sha256Hex } from "@/lib/sha256";

describe("buildTechnicalContext", () => {
  it("extracts admitted MITRE techniques, tactics, concise plain meaning, case-specific relevance, and sources", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "พบการบุกรุกเข้าสู่ IIS Web Server โดยคนร้ายใช้ Application Shimming เพื่อฝังตัว",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "assistant",
        content: "ผลการวิเคราะห์...",
        retrieval_context_id: "ret-1",
        metadata_json: {
          analysis_kind: "grounded_main_analysis",
          mitre_table: [
            {
              technique_id: "T1190",
              name: "Exploit Public-Facing Application",
              tactic: "Initial Access",
              description: "Abuse of a public-facing application to gain access.",
              reason: "คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server",
            },
            {
              technique_id: "T1546.011",
              name: "Event Triggered Execution: Application Shimming",
              tactic: "Persistence, Privilege Escalation",
              description: "Adversaries may establish persistence using application shims.",
              reason: "พบพฤติกรรมติดตั้ง Application Shim เพื่อคงสิทธิ์",
            },
          ],
          analysis_trace: {
            version: "analysis_trace_v2",
            claims: [
              {
                claim_id: "c1",
                text: "คนร้ายโจมตีผ่านช่องโหว่ IIS",
                claim_type: "event_progression",
                epistemic_status: "reported",
                source_message_ids: ["msg-1"],
              },
            ],
            mitre_associations: [
              {
                association_id: "assoc-1",
                technique_id: "T1190",
                claim_ids: ["c1"],
                reason: "คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server ที่เปิดสู่สาธารณะ",
                status: "candidate",
                support_role: "external_knowledge",
              },
            ],
          },
        },
        created_at: "2026-03-10T08:01:00Z",
      },
    ];

    const result = buildTechnicalContext(messages);
    expect(result.hasContext).toBe(true);
    expect(result.totalCount).toBe(1);

    // Technique 1: T1190 (linked through claim c1 to msg-1)
    const t1190 = result.techniques.find((t) => t.techniqueId === "T1190")!;
    expect(t1190).toBeDefined();
    expect(t1190.techniqueName).toBe("Exploit Public-Facing Application");
    expect(t1190.tactic).toBe("Initial Access");
    expect(t1190.shortPlainMeaning).toBe("Abuse of a public-facing application to gain access.");
    expect(t1190.whyRelevantHere).toContain("คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server");
    expect(t1190.caseBasisSources).toHaveLength(1);
    expect(t1190.caseBasisSources[0].id).toBe("msg-1");
    expect(t1190.isExternalReference).toBe(true);

    const retrievedOnly = result.retrievedOnlyTechniques.find((t) => t.techniqueId === "T1546.011");
    expect(retrievedOnly).toBeDefined();
    expect(result.techniques.some((t) => t.techniqueId === "T1546.011")).toBe(false);
  });

  it("proves unlinked MITRE techniques or associations linking to analyst_question get zero caseBasisSources", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "Initial incident",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "user",
        content: "Did the attacker use discovery techniques?",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "analyst_question" },
        created_at: "2026-03-10T08:05:00Z",
      },
      {
        id: "msg-3",
        thread_id: "thread-1",
        ordinal: 3,
        role: "assistant",
        content: "Analysis...",
        retrieval_context_id: "ret-1",
        metadata_json: {
          analysis_kind: "grounded_main_analysis",
          mitre_table: [
            {
              technique_id: "T1018",
              name: "Remote System Discovery",
              tactic: "Discovery",
              description: "Discovery description",
              reason: "Discovery reason",
            },
          ],
          analysis_trace: {
            version: "analysis_trace_v2",
            claims: [
              {
                claim_id: "c2",
                text: "Discovery query",
                claim_type: "event_progression",
                epistemic_status: "reported",
                source_message_ids: ["msg-2"],
              },
            ],
            mitre_associations: [
              {
                association_id: "assoc-2",
                technique_id: "T1018",
                claim_ids: ["c2"],
                reason: "Discovery note",
                status: "candidate",
                support_role: "external_knowledge",
              },
            ],
          },
        },
        created_at: "2026-03-10T08:10:00Z",
      },
    ];

    const result = buildTechnicalContext(messages);
    expect(result.techniques[0].techniqueId).toBe("T1018");
    // Since msg-2 is an analyst_question, it must NOT be included as a source
    expect(result.techniques[0].caseBasisSources).toHaveLength(0);
  });

  it("keeps raw retrieved rows separate when no validated association exists", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "พบพฤติกรรม...",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "assistant",
        content: "ผล...",
        retrieval_context_id: "ret-1",
        metadata_json: {
          analysis_kind: "grounded_main_analysis",
          mitre_table: [
            {
              technique_id: "T1018",
              name: "Remote System Discovery",
              tactic: "Discovery",
              description: "Adversaries may attempt to get a listing of other systems.",
              reason: "เทคนิคนี้ถูกนำมาใช้เป็นกรอบอ้างอิงเชิงวิเคราะห์เพื่ออธิบายพฤติกรรมการโจมตีที่สอดคล้องกับข้อมูลในสำนวนคดี",
            },
          ],
        },
        created_at: "2026-03-10T08:01:00Z",
      },
    ];

    const result = buildTechnicalContext(messages);
    expect(result.status).toBe("retrieved_without_supported_match");
    expect(result.techniques).toHaveLength(0);
    expect(result.retrievedOnlyTechniques[0].techniqueId).toBe("T1018");
  });

  it("filters out Tactics (TAxxxx) so they do not appear as standalone technique cards", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "ข้อมูลถูกเข้ารหัส",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "assistant",
        content: "ผลการวิเคราะห์...",
        retrieval_context_id: "ret-1",
        metadata_json: {
          analysis_kind: "grounded_main_analysis",
          mitre_table: [
            {
              technique_id: "T1486",
              name: "Data Encrypted for Impact",
              tactic: "Impact",
              description: "Technique description",
              reason: "การเข้ารหัสข้อมูลสมาชิก",
            },
            {
              technique_id: "TA0040",
              name: "Impact",
              tactic: "Enterprise Tactic",
              description: "Tactic description",
              reason: "",
            },
            {
              technique_id: "TA0034",
              name: "Impact",
              tactic: "ICS Tactic",
              description: "Tactic description",
              reason: "",
            },
          ],
          analysis_trace: {
            version: "analysis_trace_v2",
            claims: [
              {
                claim_id: "c1",
                text: "ข้อมูลถูกเข้ารหัส",
                claim_type: "event_progression",
                epistemic_status: "reported",
                source_message_ids: ["msg-1"],
              },
            ],
            mitre_associations: [
              {
                association_id: "assoc-1",
                technique_id: "T1486",
                claim_ids: ["c1"],
                reason: "การเข้ารหัสข้อมูลสมาชิกบนเครื่องแม่ข่าย",
                status: "candidate",
                support_role: "external_knowledge",
              },
            ],
          },
        },
        created_at: "2026-03-10T08:01:00Z",
      },
    ];

    const result = buildTechnicalContext(messages);
    expect(result.hasContext).toBe(true);
    expect(result.totalCount).toBe(1);
    expect(result.techniques).toHaveLength(1);
    expect(result.techniques[0].techniqueId).toBe("T1486");
    expect(result.techniques[0].techniqueName).toBe("Data Encrypted for Impact");
    expect(result.techniques[0].tactic).toBe("Impact");
    // Ensure TA0040 and TA0034 were filtered out
    expect(result.techniques.some((t) => t.techniqueId.startsWith("TA"))).toBe(false);
  });

  it("returns empty when no analysis message exists", () => {
    const result = buildTechnicalContext([]);
    expect(result.hasContext).toBe(false);
    expect(result.techniques).toHaveLength(0);
    expect(result.totalCount).toBe(0);
  });
});

const nativeSourceId = "11111111-1111-4111-8111-111111111111";
const nativeCaseId = "22222222-2222-4222-8222-222222222222";
const nativeSnapshotId = "33333333-3333-4333-8333-333333333333";
const nativeResultId = "44444444-4444-4444-8444-444444444444";
const nativeQuote = "The evidence reports PowerShell network activity.";

function nativeFixture(
  status: string,
  rows: Record<string, string>[],
  associations: Record<string, unknown>[] = [],
  failureCode?: string,
): { result: CaseAnalysisResultRead; snapshot: CaseEvidenceSnapshotRead } {
  const manifest = [{
    exact_text: nativeQuote,
    provenance: { origin: "analyst-authored" },
    revision: 1,
    source_id: nativeSourceId,
    source_kind: "narrative",
    text_sha256: sha256Hex(nativeQuote),
  }];
  const snapshot: CaseEvidenceSnapshotRead = {
    id: nativeSnapshotId,
    case_id: nativeCaseId,
    evidence_revision: 1,
    format_version: "case_evidence_snapshot_v1",
    manifest_json: manifest,
    input_text: nativeQuote,
    text_sha256: sha256Hex(nativeQuote),
    manifest_sha256: sha256Hex(JSON.stringify(manifest)),
    created_at: "2026-09-10T00:00:00Z",
  };
  const retrievalContextId = status === "not_applicable" ? null : "retrieval-native-1";
  const traceAssociations = associations.map((association) => ({
    association_id: association.association_id,
    technique_id: association.technique_id,
    claim_ids: association.claim_ids,
    reason: association.reason,
    status: "candidate_only",
    support_role: "external_technical_context",
  }));
  const result: CaseAnalysisResultRead = {
    id: nativeResultId,
    case_id: nativeCaseId,
    run_id: "55555555-5555-4555-8555-555555555555",
    snapshot_id: nativeSnapshotId,
    schema_version: "case_analysis_result_v1",
    status: "validated",
    answer: nativeQuote,
    summary: nativeQuote,
    trace_json: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      evidence_sha256: snapshot.text_sha256,
      summary: nativeQuote,
      claims: [{
        claim_id: "A-01",
        claim_type: "reported",
        text: nativeQuote,
        epistemic_status: "reported",
        reasoning_summary: null,
        supporting_source_ids: [nativeSourceId],
        contradicting_source_ids: [],
        supporting_citations: [{ source_id: nativeSourceId, source_revision: 1, exact_quote: nativeQuote }],
        contradicting_citations: [],
      }],
      gaps: [],
      mitre_associations: traceAssociations,
      retrieval_context_id: retrievalContextId,
    },
    execution_receipt_json: {},
    retrieval_context_id: retrievalContextId,
    pipeline_config: {},
    provider_metadata_json: {
      technical_augmentation: {
        version: "case_mitre_augmentation_v1",
        status,
        applicability: { decision: "RETRIEVE", source_message_ids: [nativeSourceId], trigger_text: [nativeQuote] },
        retrieval_context_id: retrievalContextId,
        mitre_table: rows,
        query_sha256: "a".repeat(64),
        association_ids: associations.map((association) => association.association_id),
        ...(failureCode ? { failure_code: failureCode } : {}),
      },
    },
    created_at: "2026-09-10T00:00:00Z",
    freshness: "current",
  };
  return { result, snapshot };
}

describe("buildNativeTechnicalContext", () => {
  const row = { technique_id: "T1059.001", name: "PowerShell", tactic: "Execution", description: "Command and scripting interpreter." };

  it("shows mapping failure separately from retrieved-only context", () => {
    const fixture = nativeFixture("failed", [row], [], "mitre_mapping_invalid");
    const result = buildNativeTechnicalContext(fixture.result, fixture.snapshot);
    expect(result.status).toBe("failed");
    expect(result.failureStage).toBe("mapping");
    expect(result.retrievedOnlyTechniques).toHaveLength(1);
    expect(result.techniques).toHaveLength(0);
  });

  it("distinguishes a valid retrieval with no supported match", () => {
    const fixture = nativeFixture("retrieved_without_supported_match", [row]);
    const result = buildNativeTechnicalContext(fixture.result, fixture.snapshot);
    expect(result.status).toBe("retrieved_without_supported_match");
    expect(result.techniques).toHaveLength(0);
    expect(result.retrievedOnlyCount).toBe(1);
  });

  it("renders only the mapped subset when retrieval contains partial mappings", () => {
    const fixture = nativeFixture(
      "retrieved_with_matches",
      [row, { technique_id: "T1105", name: "Ingress Tool Transfer", tactic: "Command and Control", description: "Transfer tools into the environment." }],
      [{ association_id: "MA-01", technique_id: "T1059.001", claim_ids: ["A-01"], reason: "The claim describes PowerShell activity." }],
    );
    const result = buildNativeTechnicalContext(fixture.result, fixture.snapshot);
    expect(result.status).toBe("retrieved_with_matches");
    expect(result.techniques.map((item) => item.techniqueId)).toEqual(["T1059.001"]);
    expect(result.retrievedOnlyTechniques.map((item) => item.techniqueId)).toEqual(["T1105"]);
    expect(result.techniques[0].caseBasisSources).toHaveLength(1);
  });

  it("exposes invalid trace instead of collapsing it into empty context", () => {
    const fixture = nativeFixture("retrieved_without_supported_match", [row]);
    fixture.result.trace_json = { ...(fixture.result.trace_json ?? {}), evidence_sha256: "0".repeat(64) };
    const result = buildNativeTechnicalContext(fixture.result, fixture.snapshot);
    expect(result.status).toBe("invalid_trace");
    expect(result.failureCode).toBe("invalid_trace");
  });
});
