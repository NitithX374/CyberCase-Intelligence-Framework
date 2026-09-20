import type { ChatMessageRead } from "./chatTypes";

export type AnalysisStepRead = {
    status: "need_followup" | "completed";
    round: number;
    max_rounds: number;
    stop_reason?: string | null;
    question?: FollowupQuestionRead | null;
    result?: CaseAnalysisResultRead | null;
};

export type CaseAnalysisClaim = {
    claim_id: string;
    claim_type: "reported" | "analytical_inference" | "unknown";
    text: string;
    epistemic_status: "reported" | "suspected" | "contradicted" | "not_established" | "unknown" | "not_confirmed";
    supporting_source_ids?: string[];
    contradicting_source_ids?: string[];
    supporting_citations?: CaseSourceCitation[];
    contradicting_citations?: CaseSourceCitation[];
    reasoning_summary?: string | null;
};

export type CaseAnalysisCreate = {
    response_language: "thai" | "english";
};

export type CaseAnalysisGap = {
    gap_id: string;
    gap_key: string;
    topic: string;
    status: "NOT_PROVIDED" | "EXPLICITLY_UNKNOWN" | "AMBIGUOUS" | "CONFLICTING";
    description: string;
    affected_claim_ids?: string[];
    reason: string;
    priority: "high" | "medium" | "low";
    askable: boolean;
    clarification_question?: string | null;
};

export type CaseAnalysisResultRead = {
    id: string;
    case_id: string;
    source_revision: number;
    schema_version: string;
    status: "validated";
    answer: string;
    summary: string;
    trace_json: CaseAnalysisTrace | null;
    retrieval_context_id: string | null;
    pipeline_config: {
        [key: string]: unknown;
    };
    external_context_json?: {
        [key: string]: unknown;
    };
    created_at: string;
    freshness: "missing" | "current" | "stale";
};

export type CaseAnalysisTrace = {
    version: "case_analysis_trace_v1";
    validation_status: "validated";
    analysis_mode: "case_overview" | "question_answer";
    summary: string;
    involved_parties?: CaseInvolvedParty[];
    timeline?: CaseTimelineItem[];
    claims: CaseAnalysisClaim[];
    impacts?: CaseImpactItem[];
    gaps?: CaseAnalysisGap[];
    mitre_associations?: CaseMitreAssociation[];
    retrieval_context_id?: string | null;
    grounding?: CaseGroundingReport | null;
    stop_reason?: string | null;
};

export type CaseChatResponse = {
    messages: ChatMessageRead[];
    analysis?: CaseAnalysisResultRead | null;
};

export type CaseGroundingReport = {
    claims: number;
    citations_claimed: number;
    citations_verified: number;
    citations_paraphrased: number;
    citations_unfound: number;
    claims_without_citation: number;
    claims_duplicated: number;
    associations_outside_context: number;
    sources_cited: number;
    sources_total: number;
};

export type CaseImpactItem = {
    description: string;
    claim_ids?: string[];
};

export type CaseInvolvedParty = {
    name: string;
    role: string;
    claim_ids?: string[];
};

export type CaseMitreAssociation = {
    association_id: string;
    technique_id: string;
    claim_ids: string[];
    reason: string;
    plain_meaning: string;
    status: "candidate_only";
    support_role: "external_technical_context";
};

export type CaseSourceCitation = {
    source_id: string;
    exact_quote: string;
    document_id?: string | null;
    filename?: string | null;
    page_numbers?: number[];
};

export type CaseTimelineItem = {
    time: string;
    event: string;
    claim_ids?: string[];
};

export type FollowupQuestionRead = {
    message_id: string;
    gap_id: string;
    gap_key: string;
    question: string;
};
