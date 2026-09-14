import { describe, expect, it } from "vitest";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead } from "@/lib/api";
import { buildCaseOverview } from "@/lib/case-overview-builder";

const sourceId = "11111111-1111-4111-8111-111111111111";
const caseId = "22222222-2222-4222-8222-222222222222";
const snapshotId = "33333333-3333-4333-8333-333333333333";
const quote = "The witness saw a blue vehicle.";

function fixture(): { result: CaseAnalysisResultRead; snapshot: CaseEvidenceSnapshotRead } {
  const manifest = [{
    exact_text: quote,
    provenance: { origin: "analyst-authored" },
    revision: 1,
    source_id: sourceId,
    source_kind: "narrative",
  }];
  const inputText = `[CASE NARRATIVE · SOURCE ${sourceId} · REVISION 1]\n${quote}`;
  const snapshot: CaseEvidenceSnapshotRead = {
    id: snapshotId,
    case_id: caseId,
    evidence_revision: 1,
    format_version: "case_evidence_snapshot_v1",
    manifest_json: manifest,
    input_text: inputText,
    created_at: "2026-09-10T00:00:00Z",
  };
  const result: CaseAnalysisResultRead = {
    id: "44444444-4444-4444-8444-444444444444",
    case_id: caseId,
    run_id: "55555555-5555-4555-8555-555555555555",
    evidence_revision: 1,
    schema_version: "case_analysis_result_v1",
    status: "validated",
    answer: quote,
    summary: quote,
    trace_json: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      summary: "The submitted material identifies a blue vehicle.",
      claims: [{
        claim_id: "A-01",
        claim_type: "reported",
        text: quote,
        epistemic_status: "reported",
        reasoning_summary: null,
        supporting_source_ids: [sourceId],
        contradicting_source_ids: [],
        supporting_citations: [{ source_id: sourceId, source_revision: 1, exact_quote: quote }],
        contradicting_citations: [],
      }],
      gaps: [],
      mitre_associations: [],
    },
    execution_receipt_json: {},
    retrieval_context_id: null,
    pipeline_config: {},
    provider_metadata_json: {},
    created_at: "2026-09-10T00:00:00Z",
    freshness: "current",
  };
  return { result, snapshot };
}

describe("Case overview projection", () => {
  it("renders claims from the persisted snapshot without message identifiers", () => {
    const { result, snapshot } = fixture();
    const overview = buildCaseOverview(result, snapshot, "completed");
    const source = overview.findings[0].supportingSources[0];
    expect(overview.incidentSummary).toContain("blue vehicle");
    expect(source).toMatchObject({ id: sourceId, ordinal: 1, isNativeEvidence: true, exactQuote: quote });
  });

  it("renders overview with OCR document sources", () => {
    const documentQuote = "Defendant was seen at the scene.";
    const manifest = [{
      document_id: "DOC-001",
      exact_text: documentQuote,
      filename: "report.pdf",
      provenance: {
        origin: "ocr",
        pages: [{
          end_offset: documentQuote.length,
          page_number: 1,
          regions: [{
            bbox: { x0: 0, x1: 1000, y0: 0, y1: 500 },
          }],
          start_offset: 0,
        }],
      },
      revision: 1,
      source_id: sourceId,
      source_kind: "reviewed_document",
    }];

    const snapshot: CaseEvidenceSnapshotRead = {
      id: snapshotId,
      case_id: caseId,
      evidence_revision: 1,
      format_version: "case_evidence_snapshot_v1",
      manifest_json: manifest,
      input_text: `[DOCUMENT report.pdf · SOURCE ${sourceId} · REVISION 1]\n${documentQuote}`,
      created_at: "2026-09-10T00:00:00Z",
    };
    const { result } = fixture();
    const docResult: CaseAnalysisResultRead = {
      ...result,
      trace_json: {
        ...result.trace_json,
        claims: [{
          claim_id: "A-01",
          claim_type: "reported",
          text: documentQuote,
          epistemic_status: "reported",
          reasoning_summary: null,
          supporting_source_ids: [sourceId],
          contradicting_source_ids: [],
          supporting_citations: [{
            source_id: sourceId,
            source_revision: 1,
            exact_quote: documentQuote,
            document_id: "DOC-001",
            filename: "report.pdf",
            page_numbers: [1],
          }],
          contradicting_citations: [],
        }],
      },
    };
    const overview = buildCaseOverview(docResult, snapshot, "completed");
    expect(overview.hasAnalysis).toBe(true);
    expect(overview.findings).toHaveLength(1);
    expect(overview.findings[0].supportingSources[0].pageNumbers).toEqual([1]);
  });

  it("supports citations when the quote appears multiple times on the same page", () => {
    const repeatedQuote = "Suspicious vehicle reported.";
    const fullText = `${repeatedQuote}\nSome intermediate text.\n${repeatedQuote}`;
    const manifest = [{
      document_id: "DOC-001",
      exact_text: fullText,
      filename: "report.pdf",
      provenance: {
        origin: "ocr",
        pages: [{
          end_offset: fullText.length,
          page_number: 1,
          start_offset: 0,
        }],
      },
      revision: 1,
      source_id: sourceId,
      source_kind: "reviewed_document",
    }];
    const snapshot: CaseEvidenceSnapshotRead = {
      id: snapshotId,
      case_id: caseId,
      evidence_revision: 1,
      format_version: "case_evidence_snapshot_v1",
      manifest_json: manifest,
      input_text: `[DOCUMENT report.pdf · SOURCE ${sourceId} · REVISION 1]\n${fullText}`,
      created_at: "2026-09-10T00:00:00Z",
    };
    const { result } = fixture();
    const docResult: CaseAnalysisResultRead = {
      ...result,
      trace_json: {
        ...result.trace_json,
        claims: [{
          claim_id: "A-01",
          claim_type: "reported",
          text: repeatedQuote,
          epistemic_status: "reported",
          reasoning_summary: null,
          supporting_source_ids: [sourceId],
          contradicting_source_ids: [],
          supporting_citations: [{
            source_id: sourceId,
            source_revision: 1,
            exact_quote: repeatedQuote,
            document_id: "DOC-001",
            filename: "report.pdf",
            page_numbers: [1],
          }],
          contradicting_citations: [],
        }],
      },
    };
    const overview = buildCaseOverview(docResult, snapshot, "completed");
    expect(overview.hasAnalysis).toBe(true);
    expect(overview.findings).toHaveLength(1);
    expect(overview.findings[0].supportingSources[0].pageNumbers).toEqual([1]);
  });
});
