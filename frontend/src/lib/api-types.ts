export type ThreadStatus =
  | "idle"
  | "processing"
  | "awaiting_followup"
  | "answered"
  | "failed";

export type ChatMessageAction = "ask" | "add_case_info";

export type RunStatus = "queued" | "running" | "completed" | "failed";

export interface ChatThreadRead {
  id: string;
  title: string;
  status: ThreadStatus;
  created_at: string;
  updated_at: string;
}

export interface PersistedChatMessage {
  id: string;
  thread_id: string;
  ordinal: number;
  role: "user" | "assistant";
  content: string;
  retrieval_context_id: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
}

export interface ChatThreadDetail extends ChatThreadRead {
  messages: PersistedChatMessage[];
}

export interface ChatRun {
  id: string;
  thread_id: string;
  request_message_id: string;
  operation: "query" | "resume";
  status: RunStatus;
  error_code: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessageAccepted {
  message: PersistedChatMessage;
  run: ChatRun;
}

export type ChatReportSupportType =
  | "user_reported"
  | "extraction_candidate"
  | "general_technical_knowledge"
  | "mitre_mapping_candidate"
  | "unknown";

export interface ChatReportClaim {
  claim_id: string;
  section_id: string;
  text: string;
  support_type: ChatReportSupportType;
  evidence_ids: string[];
  timeline_event_ids: string[];
  mitre_technique_ids: string[];
}

export interface ChatReportSection {
  section_id: string;
  heading: string;
  paragraphs: string[];
  items: string[];
}

export interface ChatStructuredReport {
  report_version:
    | "baseline_report_v1"
    | "preliminary_analysis_report_v1";
  status: "provisional_unverified";
  title: string;
  sections: ChatReportSection[];
  claims: ChatReportClaim[];
  limitations: string[];
}

export interface ChatReportRead {
  report_id: string;
  thread_id: string;
  version_number: number;
  idempotency_key: string;
  source_snapshot_hash: string;
  extraction_id: string;
  extraction_version: string;
  prompt_version: string;
  provider: string;
  model: string;
  decoding_settings: Record<string, unknown>;
  persistence_status: "completed" | "failed";
  validation_status: "validated" | "failed";
  report: ChatStructuredReport | null;
  validation_errors: string[];
  failure_code: string | null;
  failure_message: string | null;
  created_at: string;
  finished_at: string | null;
  latency_ms: number | null;
  input_tokens: number | null;
  output_tokens: number | null;
}

export type {
  ChatBaselineEntity,
  ChatBaselineEvidence,
  ChatBaselineExtraction,
  ChatBaselineExtractionFailure,
  ChatBaselineMissingInformation,
  ChatBaselineRelationship,
  ChatBaselineTimelineEvent,
  ChatCaseState,
  ChatExtraction,
  ChatExtractionConfidence,
  ChatRelationshipStatus,
  ChatReportedStatus,
} from "@/lib/metadata-schemas";
