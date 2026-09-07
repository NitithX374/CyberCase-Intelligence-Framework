export type ChatActionMetadata = {
    action?: "initial_analysis" | "ask" | "add_case_info";
    route?: string;
    rag_invoked?: boolean;
    retrieval_context_reused?: boolean;
    analysis_mode?: "case_overview" | "question_answer";
    prompt_version?: string;
} & {
    [key: string]: unknown;
};
