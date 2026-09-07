export type FollowUpMetadata = {
    kind?: "clarification" | "decision";
    action?: "ask_followup" | "proceed";
    question?: string;
    reason_code?: string;
    source_run_id?: string;
    root_ordinal?: number;
    round?: number;
    prior_exchange_count?: number;
    followup_context?: {
        [key: string]: string;
    } | null;
    gap_analysis?: {
        [key: string]: unknown;
    };
    rag_invoked?: boolean;
    rag_skipped?: boolean;
    failure_code?: string | null;
} & {
    [key: string]: unknown;
};
