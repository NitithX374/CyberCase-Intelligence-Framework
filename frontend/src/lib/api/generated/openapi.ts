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
    "/api/v1/auth/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["get_me_api_v1_auth_me_get"];
        put?: never;
        post?: never;
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
    "/api/v1/auth/dev-login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post: operations["dev_login_api_v1_auth_dev_login_post"];
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
    "/api/v1/cases/{case_id}/documents": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get: operations["list_case_documents_api_v1_cases__case_id__documents_get"];
        put?: never;
        post: operations["add_case_document_api_v1_cases__case_id__documents_post"];
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
            round: number;
            max_rounds: number;
            stop_reason?: string | null;
            question?: components["schemas"]["FollowupQuestionRead"] | null;
            result?: components["schemas"]["CaseAnalysisResultRead"] | null;
        };
        AuthTokenResponse: {
            access_token: string;
            token_type: string;
            expires_in: number;
            user: components["schemas"]["UserRead"];
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
            reasoning_summary?: string | null;
        };
        CaseAnalysisCreate: {
            response_language: "thai" | "english";
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
            schema_version: string;
            status: "validated";
            summary: string;
            trace_json: components["schemas"]["CaseAnalysisTrace"] | null;
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
        CaseAnalysisTrace: {
            version: "case_analysis_trace_v1";
            validation_status: "validated";
            analysis_mode: "case_overview" | "question_answer";
            summary: string;
            involved_parties?: components["schemas"]["CaseInvolvedParty"][];
            timeline?: components["schemas"]["CaseTimelineItem"][];
            claims: components["schemas"]["CaseAnalysisClaim"][];
            impacts?: components["schemas"]["CaseImpactItem"][];
            gaps?: components["schemas"]["CaseAnalysisGap"][];
            mitre_associations?: components["schemas"]["CaseMitreAssociation"][];
            retrieval_context_id?: string | null;
            grounding?: components["schemas"]["CaseGroundingReport"] | null;
            stop_reason?: string | null;
        };
        CaseChatRead: {
            case_id: string;
            status: "idle" | "answered";
            messages?: components["schemas"]["ChatMessageRead"][];
        };
        CaseChatResponse: {
            messages: components["schemas"]["ChatMessageRead"][];
            analysis?: components["schemas"]["CaseAnalysisResultRead"] | null;
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
            citations_paraphrased: number;
            citations_unfound: number;
            claims_without_citation: number;
            claims_duplicated: number;
            citations_duplicated: number;
            associations_outside_context: number;
            associations_without_claim: number;
            sources_cited: number;
            sources_total: number;
        };
        CaseImpactItem: {
            description: string;
            claim_ids?: string[];
        };
        CaseInvolvedParty: {
            name: string;
            role: string;
            claim_ids?: string[];
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
        CaseRead: {
            id: string;
            user_id?: string | null;
            title: string;
            status: "idle" | "answered";
            source_revision: number;
            latest_analysis_result_id?: string | null;
            analysis_freshness: "missing" | "current" | "stale";
            created_at: string;
            updated_at: string;
        };
        CaseReportCreate: {
            analysis_result_id?: string | null;
        };
        CaseReportRead: {
            report_id: string;
            version_number: number;
            case_id: string;
            analysis_result_id: string;
            report: components["schemas"]["StructuredReport"];
            created_at: string;
        };
        CaseSourceCitation: {
            source_id: string;
            exact_quote: string;
            document_id?: string | null;
            filename?: string | null;
            page_numbers?: number[];
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
            exact_text: string;
            provenance_json?: {
                [key: string]: unknown;
            };
            source_metadata_json?: {
                [key: string]: unknown;
            };
            created_at: string;
            archived_at: string | null;
        };
        CaseTimelineItem: {
            time: string;
            event: string;
            claim_ids?: string[];
        };
        CaseUpdate: {
            title: string;
        };
        ChatMessageCreate: {
            content: string;
            client_request_id?: string | null;
            response_language: "thai" | "english";
        };
        ChatMessageRead: {
            id: string;
            case_id: string;
            ordinal: number;
            role: "user" | "assistant";
            content: string;
            message_kind: "conversation" | "followup_question" | "followup_answer";
            gap_key?: string | null;
            analysis_result_id: string | null;
            in_reply_to_message_id?: string | null;
            metadata_json: components["schemas"]["MessageMetadata"];
            created_at: string;
        };
        DevLoginRequest: {
            email: string;
            name: string;
        };
        FollowupQuestionRead: {
            message_id: string;
            gap_id: string;
            gap_key: string;
            question: string;
        };
        HTTPValidationError: {
            detail?: components["schemas"]["ValidationError"][];
        };
        MessageMetadata: {
            action?: "conversation";
            analysis_trace?: {
                [key: string]: unknown;
            };
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
        ReportClaim: {
            claim_id: string;
            section_id: "case_summary" | "case_evidence" | "mitre_attack_mapping" | "mapping_rationale" | "evidence_to_examine" | "preliminary_recommendations" | "system_limitations";
            text: string;
            support_type: "user_reported" | "analytical_inference" | "unknown";
            source_ids?: string[];
            mitre_technique_ids?: string[];
        };
        ReportSection: {
            section_id: "case_summary" | "case_evidence" | "mitre_attack_mapping" | "mapping_rationale" | "evidence_to_examine" | "preliminary_recommendations" | "system_limitations";
            heading: string;
            paragraphs?: string[];
            items?: string[];
        };
        StructuredReport: {
            report_version: "preliminary_analysis_report_v1";
            status: "provisional_unverified";
            title: string;
            sections: components["schemas"]["ReportSection"][];
            claims?: components["schemas"]["ReportClaim"][];
            limitations?: string[];
        };
        UserRead: {
            id: string;
            email: string;
            name: string;
            oauth_provider: string;
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
    get_me_api_v1_auth_me_get: {
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
                    "application/json": components["schemas"]["UserRead"];
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
    dev_login_api_v1_auth_dev_login_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["DevLoginRequest"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthTokenResponse"];
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
    list_case_documents_api_v1_cases__case_id__documents_get: {
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
                    "application/json": components["schemas"]["CaseDocumentRead"][];
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
        requestBody: {
            content: {
                "application/json": components["schemas"]["CaseAnalysisCreate"];
            };
        };
        responses: {
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AnalysisStepRead"];
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
