export interface paths {
    "/api/v1/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["health_check_api_v1_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/register": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["register_api_v1_auth_register_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["login_api_v1_auth_login_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/session": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["get_session_api_v1_auth_session_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/logout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["logout_api_v1_auth_logout_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["list_cases_api_v1_cases_get"];
        put?: never;
        post: operations["create_case_api_v1_cases_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["get_case_api_v1_cases__case_id__get"];
        put?: never;
        post?: never;
        delete: operations["delete_case_api_v1_cases__case_id__delete"];
        options?: never;
        head?: never;
        patch: operations["update_case_api_v1_cases__case_id__patch"];
        trace?: never;
    };
    "/api/v1/cases/{case_id}/chat": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["get_case_chat_api_v1_cases__case_id__chat_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}/chat/messages": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["create_case_chat_message_api_v1_cases__case_id__chat_messages_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}/documents/{document_id}/content": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["get_case_document_content_api_v1_cases__case_id__documents__document_id__content_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}/documents": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["add_case_document_api_v1_cases__case_id__documents_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}/sources": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["list_case_sources_api_v1_cases__case_id__sources_get"];
        put?: never;
        post: operations["add_case_source_api_v1_cases__case_id__sources_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}/analysis": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["get_latest_analysis_api_v1_cases__case_id__analysis_get"];
        put?: never;
        post: operations["analyse_case_api_v1_cases__case_id__analysis_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}/reports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["list_case_reports_api_v1_cases__case_id__reports_get"];
        put?: never;
        post: operations["generate_case_report_api_v1_cases__case_id__reports_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}/reports/{report_id}/pdf": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["download_case_report_pdf_api_v1_cases__case_id__reports__report_id__pdf_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/cases/{case_id}/reports/{report_id}/html": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["render_case_report_html_api_v1_cases__case_id__reports__report_id__html_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        AnalysisStepRead: {
            status: "need_followup" | "completed";
            result?: components["schemas"]["CaseAnalysisResultRead"] | null;
        };
        Body_add_case_document_api_v1_cases__case_id__documents_post: {
            file: string;
        };
        CaseAnalysisClaim: {
            claim_id: string;
            claim_type: "reported" | "analytical_inference" | "unknown";
            text: string;
            epistemic_status: "reported" | "suspected" | "contradicted" | "not_established" | "unknown" | "not_confirmed";
            supporting_source_ids?: string[];
            contradicting_source_ids?: string[];
            supporting_citations?: components["schemas"]["CaseSourceCitation"][];
            contradicting_citations?: components["schemas"]["CaseSourceCitation"][];
            unverified_citations?: components["schemas"]["CaseUnverifiedCitation"][];
            invalid_evidence?: components["schemas"]["CaseInvalidEvidence"][];
            reasoning_summary?: string | null;
        };
        CaseAnalysisGap: {
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
        CaseAnalysisResultRead: {
            id: string;
            case_id: string;
            source_revision: number;
            schema_version: "case_analysis_trace_v1";
            status: "validated";
            summary: string;
            trace_json: components["schemas"]["CaseAnalysisTrace"] | null;
            pipeline_config: {
                [key: string]: unknown;
            };
            external_context_json?: {
                [key: string]: unknown;
            };
            created_at: string;
            freshness: "missing" | "current" | "stale";
            readonly retrieval_context_id: string | null;
        };
        CaseAnalysisTrace: {
            version: "case_analysis_trace_v1";
            validation_status: "validated";
            analysis_mode: "case_overview" | "question_answer";
            summary: string;
            summary_units?: components["schemas"]["CaseSummaryUnit"][];
            involved_parties?: components["schemas"]["CaseInvolvedParty"][];
            timeline?: components["schemas"]["CaseTimelineItem"][];
            claims: components["schemas"]["CaseAnalysisClaim"][];
            impacts?: components["schemas"]["CaseImpactItem"][];
            gaps?: components["schemas"]["CaseAnalysisGap"][];
            mitre_associations?: components["schemas"]["CaseMitreAssociation"][];
            retrieval_context_id?: string | null;
            grounding?: components["schemas"]["CaseGroundingReport"] | null;
            view_extraction?: components["schemas"]["CaseViewExtraction"] | null;
            stop_reason?: string | null;
        };
        CaseChatRead: {
            case_id: string;
            messages?: components["schemas"]["ChatMessageRead"][];
            pending_question_id?: string | null;
        };
        CaseChatResponse: {
            messages: components["schemas"]["ChatMessageRead"][];
            pending_question_id?: string | null;
            analysis?: components["schemas"]["CaseAnalysisResultRead"] | null;
        };
        CaseClaimSpan: {
            claim_id: string;
            start: number;
            end: number;
        };
        CaseCreate: {
            title: string;
        };
        CaseDocumentRead: {
            id: string;
            case_id: string;
            filename: string;
            mime_type: string;
            size_bytes: number;
            created_at: string;
        };
        CaseGroundingReport: {
            claims: number;
            citations_claimed: number;
            citations_verified: number;
            citations_pointed: number;
            citations_unfound: number;
            claims_without_citation: number;
            claims_duplicated: number;
            citations_duplicated: number;
            citations_marked: number;
            citations_meaning_pointed: number;
            evidence_ids_claimed: number;
            evidence_ids_resolved: number;
            evidence_ids_invalid: number;
            evidence_id_resolution_rate?: number | null;
            claims_with_direct_evidence: number;
            claims_with_recovered_evidence: number;
            claims_without_resolved_evidence: number;
            meaning_pointer_eligible: number;
            meaning_pointer_attempted: number;
            meaning_pointer_unavailable: number;
            meaning_pointer_unavailable_reason?: string | null;
            meaning_pointer_skipped: number;
            associations_outside_context: number;
            associations_without_claim: number;
            summary_ids_unknown: number;
            sources_cited: number;
            sources_total: number;
        };
        CaseImpactItem: {
            description: string;
            claim_ids?: string[];
            support?: ("bound" | "mixed" | "unbound" | "no_claim") | null;
            projection_grounding?: components["schemas"]["CaseProjectionGrounding"] | null;
            field_spans?: {
                [key: string]: components["schemas"]["CaseClaimSpan"];
            };
        };
        CaseInvalidEvidence: {
            source_id: string;
            evidence_unit_id: string;
            role: "supporting" | "contradicting";
            pointer_state: "unresolved";
            reason: "unknown_source" | "malformed_id" | "cross_source" | "stale_id" | "unknown_unit" | "empty_unit" | "duplicate_id";
        };
        CaseInvolvedParty: {
            name: string;
            role?: string | null;
            claim_ids?: string[];
            support?: ("bound" | "mixed" | "unbound" | "no_claim") | null;
            projection_grounding?: components["schemas"]["CaseProjectionGrounding"] | null;
            field_spans?: {
                [key: string]: components["schemas"]["CaseClaimSpan"];
            };
        };
        CaseMeaningPassage: {
            source_text: string;
            start: number;
            end: number;
            entailment: number;
            model: string;
        };
        CaseMitreAssociation: {
            association_id: string;
            technique_id: string;
            claim_ids: string[];
            reason: string;
            plain_meaning: string;
            status: "candidate_only";
            support_role: "external_technical_context";
        };
        CaseNearPassage: {
            source_text: string;
            differences?: components["schemas"]["CaseQuoteDifference"][];
            occurrences: number;
        };
        CaseProjectionGrounding: {
            verdict: "supported" | "not_supported" | "unassessed";
            reason: string;
            model?: string | null;
            entailment?: number | null;
        };
        CaseQuoteContext: {
            before: string;
            after: string;
            cut_before: boolean;
            cut_after: boolean;
        };
        CaseQuoteDifference: {
            written: string;
            source: string;
        };
        CaseRead: {
            id: string;
            user_id?: string | null;
            title: string;
            source_revision: number;
            latest_analysis_result_id?: string | null;
            analysis_freshness: "missing" | "current" | "stale";
            created_at: string;
            updated_at: string;
        };
        CaseReportContent: {
            version: "case_report_content_v1";
            title: string;
            analysed?: string | null;
            summary: string;
            views_derived_from_claims: boolean;
            summary_units?: components["schemas"]["ReportSummaryUnit"][];
            parties?: components["schemas"]["ReportParty"][];
            timeline?: components["schemas"]["ReportEvent"][];
            impacts?: components["schemas"]["ReportImpact"][];
            findings?: components["schemas"]["ReportFinding"][];
            techniques?: components["schemas"]["ReportTechnique"][];
            techniques_matched: boolean;
            mapping_note?: string | null;
            rationale_note?: string | null;
            gaps?: components["schemas"]["ReportGap"][];
            recommendations?: string[];
            limitations?: string[];
            sources?: components["schemas"]["ReportSource"][];
        };
        CaseReportCreate: {
            analysis_result_id?: string | null;
        };
        CaseReportRead: {
            report_id: string;
            version_number: number;
            case_id: string;
            analysis_result_id: string;
            report: components["schemas"]["CaseReportContent"];
            created_at: string;
        };
        CaseReviewFlag: {
            kind: "meaning_mark";
            verdict: "rule_warning";
            detail: string;
        };
        CaseSourceCitation: {
            source_id: string;
            exact_quote: string;
            evidence_unit_ids?: string[];
            pointer_state?: "direct" | "recovered" | "unresolved";
            start?: number | null;
            end?: number | null;
            document_id?: string | null;
            filename?: string | null;
            page_numbers?: number[];
            context?: components["schemas"]["CaseQuoteContext"] | null;
            tolerated_differences?: components["schemas"]["CaseQuoteDifference"][];
            review_flags?: components["schemas"]["CaseReviewFlag"][];
        };
        CaseSourceCreate: {
            exact_text: string;
            provenance_json?: {
                [key: string]: unknown;
            };
            source_kind: "narrative";
            source_metadata_json?: {
                [key: string]: unknown;
            };
        };
        CaseSourceRead: {
            id: string;
            case_id: string;
            source_kind: string;
            document_id: string | null;
            filename?: string | null;
            mime_type?: string | null;
            size_bytes?: number | null;
            exact_text: string;
            provenance_json?: {
                [key: string]: unknown;
            };
            source_metadata_json?: {
                [key: string]: unknown;
            };
            created_at: string;
        };
        CaseSummaryUnit: {
            text: string;
            claim_ids?: string[];
            support: "bound" | "mixed" | "unbound" | "no_claim";
        };
        CaseTimelineItem: {
            time: string;
            event: string;
            claim_ids?: string[];
            support?: ("bound" | "mixed" | "unbound" | "no_claim") | null;
            projection_grounding?: components["schemas"]["CaseProjectionGrounding"] | null;
            field_spans?: {
                [key: string]: components["schemas"]["CaseClaimSpan"];
            };
        };
        CaseUnverifiedCitation: {
            source_id: string;
            role: "supporting" | "contradicting";
            written_quote: string;
            evidence_unit_id?: string | null;
            near_passage?: components["schemas"]["CaseNearPassage"] | null;
            meaning_passage?: components["schemas"]["CaseMeaningPassage"] | null;
        };
        CaseUpdate: {
            title: string;
        };
        CaseViewExtraction: {
            method: "gliner2";
            model: string;
            revision: string;
            library_version: string;
            device: string;
            threshold: number;
            input_claim_ids: string[];
            excluded_claim_ids: string[];
            duration_ms: number;
        };
        ChatAnswerUnit: {
            text: string;
            basis: "case_fact" | "interpretation" | "technical" | "general";
            claim_ids?: string[];
            supporting_source_ids?: string[];
            supporting_citations?: components["schemas"]["CaseSourceCitation"][];
            contradicting_source_ids?: string[];
            contradicting_citations?: components["schemas"]["CaseSourceCitation"][];
        };
        ChatMessageCreate: {
            content: string;
            client_request_id?: string | null;
        };
        ChatMessageRead: {
            id: string;
            case_id: string;
            ordinal: number;
            role: "user" | "assistant";
            content: string;
            message_kind: "conversation" | "followup_question" | "followup_answer";
            gap_key?: string | null;
            qa_id?: string | null;
            analysis_result_id: string | null;
            in_reply_to_message_id?: string | null;
            metadata_json: components["schemas"]["MessageMetadata"];
            created_at: string;
        };
        HTTPValidationError: {
            detail?: components["schemas"]["ValidationError"][];
        };
        MessageAnalysisTrace: {
            version: "case_analysis_trace_v1";
            validation_status: "validated";
            analysis_mode: "case_overview" | "question_answer";
            summary: string;
            claims: components["schemas"]["CaseAnalysisClaim"][];
            grounding?: components["schemas"]["CaseGroundingReport"] | null;
        };
        MessageMetadata: {
            analysis_trace?: components["schemas"]["MessageAnalysisTrace"];
            answer_units?: components["schemas"]["ChatAnswerUnit"][];
            suggestion?: "none" | "add_source" | "run_analysis";
        };
        PasswordLoginRequest: {
            email: string;
            password: string;
        };
        RegisterRequest: {
            email: string;
            password: string;
            name: string;
        };
        ReportEvent: {
            time: string;
            event: string;
            references?: string[];
            support?: ("bound" | "mixed" | "unbound" | "no_claim") | null;
            projection_grounding?: components["schemas"]["CaseProjectionGrounding"] | null;
        };
        ReportFinding: {
            ordinal: number;
            text: string;
            status: string;
            is_inference: boolean;
            source_labels?: string[];
            contradicting_source_labels?: string[];
            supporting_quotes?: string[];
            contradicting_quotes?: string[];
            supporting_contexts?: (components["schemas"]["ReportQuoteContext"] | null)[];
            contradicting_contexts?: (components["schemas"]["ReportQuoteContext"] | null)[];
            supporting_tolerated?: components["schemas"]["ReportPlace"][][];
            contradicting_tolerated?: components["schemas"]["ReportPlace"][][];
            supporting_marked?: components["schemas"]["ReportMark"][][];
            contradicting_marked?: components["schemas"]["ReportMark"][][];
            unverified_quotes?: components["schemas"]["ReportUnverifiedQuote"][];
            reasoning_summary?: string | null;
        };
        ReportGap: {
            topic: string;
            priority: string;
            status: string;
            description: string;
            reason: string;
        };
        ReportImpact: {
            description: string;
            references?: string[];
            support?: ("bound" | "mixed" | "unbound" | "no_claim") | null;
            projection_grounding?: components["schemas"]["CaseProjectionGrounding"] | null;
        };
        ReportMark: {
            marks: string;
            place: "ignored" | "edge";
        };
        ReportParty: {
            name: string;
            role: string | null;
            claim_context?: string[];
            references?: string[];
            support?: ("bound" | "mixed" | "unbound" | "no_claim") | null;
            projection_grounding?: components["schemas"]["CaseProjectionGrounding"] | null;
        };
        ReportPlace: {
            written: string;
            source: string;
        };
        ReportQuoteContext: {
            before: string;
            after: string;
            cut_before: boolean;
            cut_after: boolean;
        };
        ReportSource: {
            label: string;
            kind: string;
            detail: string;
        };
        ReportSummaryUnit: {
            text: string;
            references?: number[];
            support: "bound" | "mixed" | "unbound" | "no_claim";
        };
        ReportTechnique: {
            technique_id: string;
            name: string;
            tactic: string;
            meaning: string;
            reason: string;
            findings?: number[];
            references?: string[];
        };
        ReportUnverifiedQuote: {
            written_quote: string;
            evidence_unit_id?: string | null;
            places?: components["schemas"]["ReportPlace"][];
            meaning_passage?: string | null;
        };
        UserRead: {
            id: string;
            email: string;
            name: string;
            created_at: string;
        };
        ValidationError: {
            loc: (string | number)[];
            msg: string;
            type: string;
            input?: unknown;
            ctx?: Record<string, never>;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    health_check_api_v1_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    register_api_v1_auth_register_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RegisterRequest"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    login_api_v1_auth_login_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PasswordLoginRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_session_api_v1_auth_session_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRead"] | null;
                };
            };
        };
    };
    logout_api_v1_auth_logout_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: string;
                    };
                };
            };
        };
    };
    list_cases_api_v1_cases_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseRead"][];
                };
            };
        };
    };
    create_case_api_v1_cases_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CaseCreate"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_case_api_v1_cases__case_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_case_api_v1_cases__case_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_case_api_v1_cases__case_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CaseUpdate"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_case_chat_api_v1_cases__case_id__chat_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseChatRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_case_chat_message_api_v1_cases__case_id__chat_messages_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChatMessageCreate"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseChatResponse"];
                    "text/event-stream": unknown;
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_case_document_content_api_v1_cases__case_id__documents__document_id__content_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
                document_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    add_case_document_api_v1_cases__case_id__documents_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_add_case_document_api_v1_cases__case_id__documents_post"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseDocumentRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_case_sources_api_v1_cases__case_id__sources_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseSourceRead"][];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    add_case_source_api_v1_cases__case_id__sources_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CaseSourceCreate"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseSourceRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_latest_analysis_api_v1_cases__case_id__analysis_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseAnalysisResultRead"] | null;
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    analyse_case_api_v1_cases__case_id__analysis_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AnalysisStepRead"];
                    "text/event-stream": unknown;
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_case_reports_api_v1_cases__case_id__reports_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseReportRead"][];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    generate_case_report_api_v1_cases__case_id__reports_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CaseReportCreate"];
            };
        };
        responses: {
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CaseReportRead"];
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    download_case_report_pdf_api_v1_cases__case_id__reports__report_id__pdf_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
                report_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    render_case_report_html_api_v1_cases__case_id__reports__report_id__html_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                case_id: string;
                report_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "text/html": string;
                };
            };
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
}
