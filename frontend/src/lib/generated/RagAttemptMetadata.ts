export type RagAttemptMetadata = {
    status?: "used" | "no_applicable_context" | "unavailable";
    failure_code?: string | null;
} & {
    [key: string]: unknown;
};
