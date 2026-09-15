import { describe, expect, it } from "vitest";
import type { CaseAnalysisResultRead, EvidenceSourceRead } from "@/lib/api";
import { buildCaseOverview } from "@/lib/caseOverview";

const sourceId = "11111111-1111-4111-8111-111111111111";
const caseId = "22222222-2222-4222-8222-222222222222";
const quote = "The witness saw a blue vehicle.";

function evidence(text: string, kind = "narrative", options: Record<string, unknown> = {}): EvidenceSourceRead {
  return {
    id: sourceId,
    case_id: caseId,
    source_kind: kind,
    document_id: typeof options.document_id === "string" ? options.document_id : null,
    origin_message_id: null,
    exact_text: text,
    provenance_json: (options.provenance_json as Record<string, unknown> | undefined) ?? {},
    source_metadata_json: (options.source_metadata_json as Record<string, unknown> | undefined) ?? {},
    created_at: "2026-09-10T00:00:00Z",
    archived_at: null,
  };
}

function result(text: string, citation: Record<string, unknown>): CaseAnalysisResultRead {
  return {
    id: "44444444-4444-4444-8444-444444444444",
    case_id: caseId,
    run_id: "55555555-5555-4555-8555-555555555555",
    evidence_revision: 1,
    schema_version: "case_analysis_trace_v1",
    status: "validated",
    answer: text,
    summary: text,
    trace_json: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      summary: "The submitted material identifies a blue vehicle.",
      claims: [{
        claim_id: "A-01",
        claim_type: "reported",
        text,
        epistemic_status: "reported",
        reasoning_summary: null,
        supporting_source_ids: [sourceId],
        contradicting_source_ids: [],
        supporting_citations: [citation],
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
}

describe("Case overview projection", () => {
  it("renders claims from current Case evidence", () => {
    const overview = buildCaseOverview(result(quote, { source_id: sourceId, exact_quote: quote }), [evidence(quote)], "completed");
    const source = overview.findings[0].supportingSources[0];
    expect(overview.incidentSummary).toContain("blue vehicle");
    expect(source).toMatchObject({ id: sourceId, ordinal: 1, isNativeEvidence: true, exactQuote: quote });
  });

  it("renders overview with OCR document evidence", () => {
    const documentQuote = "Defendant was seen at the scene.";
    const documentEvidence = evidence(documentQuote, "document", {
      document_id: "DOC-001",
      provenance_json: {
        pages: [{ end_offset: documentQuote.length, page_number: 1, start_offset: 0 }],
      },
      source_metadata_json: { filename: "report.pdf" },
    });
    const documentResult = result(documentQuote, {
      source_id: sourceId,
      exact_quote: documentQuote,
      document_id: "DOC-001",
      filename: "report.pdf",
      page_numbers: [1],
    });
    const overview = buildCaseOverview(documentResult, [documentEvidence], "completed");
    expect(overview.hasAnalysis).toBe(true);
    expect(overview.findings[0].supportingSources[0].pageNumbers).toEqual([1]);
  });

  it("supports repeated quotes when page binding is unambiguous", () => {
    const repeatedQuote = "Suspicious vehicle reported.";
    const fullText = `${repeatedQuote}\nSome intermediate text.\n${repeatedQuote}`;
    const documentEvidence = evidence(fullText, "document", {
      document_id: "DOC-001",
      provenance_json: { pages: [{ end_offset: fullText.length, page_number: 1, start_offset: 0 }] },
      source_metadata_json: { filename: "report.pdf" },
    });
    const documentResult = result(repeatedQuote, {
      source_id: sourceId,
      exact_quote: repeatedQuote,
      document_id: "DOC-001",
      filename: "report.pdf",
      page_numbers: [1],
    });
    const overview = buildCaseOverview(documentResult, [documentEvidence], "completed");
    expect(overview.hasAnalysis).toBe(true);
    expect(overview.findings[0].supportingSources[0].pageNumbers).toEqual([1]);
  });
});
