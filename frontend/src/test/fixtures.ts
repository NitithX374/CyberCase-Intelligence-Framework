import type {
  CaseAnalysisClaim,
  CaseAnalysisResultRead,
  CaseAnalysisTrace,
  CaseMitreAssociation,
  CaseSourceRead,
  ChatMessageRead,
} from "@/lib/api";

export const caseId = "22222222-2222-4222-8222-222222222222";
export const sourceId = "11111111-1111-4111-8111-111111111111";
export const analysisId = "44444444-4444-4444-8444-444444444444";

export function narrativeSource(
  text: string,
  overrides: Partial<CaseSourceRead> = {},
): CaseSourceRead {
  return {
    id: sourceId,
    case_id: caseId,
    source_kind: "narrative",
    document_id: null,
    filename: null,
    exact_text: text,
    provenance_json: {},
    source_metadata_json: {},
    created_at: "2026-09-10T00:00:00Z",
    ...overrides,
  };
}

export function pagedDocumentSource(
  text: string,
  pageNumber: number,
  overrides: Partial<CaseSourceRead> = {},
): CaseSourceRead {
  return narrativeSource(text, {
    source_kind: "document",
    document_id: "DOC-1",
    filename: "statement.pdf",
    provenance_json: {
      pages: [{ page_number: pageNumber, start_offset: 0, end_offset: text.length }],
    },
    ...overrides,
  });
}

export function followupExchange(
  question: string,
  answer: string,
  gapKey = "topic:incident-time",
  qaId = "QA-01",
): ChatMessageRead[] {
  return [
    {
      id: "question-1",
      case_id: caseId,
      ordinal: 1,
      role: "assistant",
      content: question,
      message_kind: "followup_question",
      gap_key: gapKey,
      qa_id: qaId,
      analysis_result_id: null,
      in_reply_to_message_id: null,
      metadata_json: {},
      created_at: "2026-09-10T00:01:00Z",
    },
    {
      id: "answer-1",
      case_id: caseId,
      ordinal: 2,
      role: "user",
      content: answer,
      message_kind: "followup_answer",
      gap_key: null,
      qa_id: qaId,
      analysis_result_id: null,
      in_reply_to_message_id: "question-1",
      metadata_json: {},
      created_at: "2026-09-10T00:02:00Z",
    },
  ];
}

export function followupHistory(
  question: string,
  answer: string,
  qaId = "QA-01",
  gapKey = "topic:incident-time",
) {
  return {
    version: "followup_snapshot_v1",
    items: [{ qa_id: qaId, gap_key: gapKey, question, answer }],
  };
}

export function sourcesRead(...sourceIds: string[]) {
  return { version: "sources_read_v1", source_ids: sourceIds };
}

export function claim(
  text: string,
  citedSourceId = sourceId,
  overrides: Partial<CaseAnalysisClaim> = {},
): CaseAnalysisClaim {
  return {
    claim_id: "A-01",
    claim_type: "reported",
    text,
    epistemic_status: "reported",
    reasoning_summary: null,
    supporting_source_ids: [citedSourceId],
    contradicting_source_ids: [],
    supporting_citations: [{ source_id: citedSourceId, exact_quote: text }],
    contradicting_citations: [],
    ...overrides,
  };
}

export function association(
  techniqueId: string,
  overrides: Partial<CaseMitreAssociation> = {},
): CaseMitreAssociation {
  return {
    association_id: "MA-01",
    technique_id: techniqueId,
    claim_ids: ["A-01"],
    reason: "The claim describes the technique.",
    plain_meaning: "",
    status: "candidate_only",
    support_role: "external_technical_context",
    ...overrides,
  };
}

export function trace(overrides: Partial<CaseAnalysisTrace> = {}): CaseAnalysisTrace {
  return {
    version: "case_analysis_trace_v1",
    validation_status: "validated",
    analysis_mode: "case_overview",
    summary: "",
    claims: [],
    gaps: [],
    mitre_associations: [],
    ...overrides,
  };
}

export function analysisResult(
  overrides: Partial<CaseAnalysisResultRead> = {},
): CaseAnalysisResultRead {
  return {
    id: analysisId,
    case_id: caseId,
    source_revision: 1,
    schema_version: "case_analysis_trace_v1",
    status: "validated",
    summary: "",
    trace_json: null,
    retrieval_context_id: null,
    pipeline_config: {},
    external_context_json: {},
    created_at: "2026-09-10T00:00:00Z",
    freshness: "current",
    ...overrides,
  };
}
