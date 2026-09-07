import type { ChatMessageCreate } from "./generated/ChatMessageCreate";
import type { ChatMessageRead } from "./generated/ChatMessageRead";
import type { ChatRunRead } from "./generated/ChatRunRead";
import type { ChatThreadRead as ThreadRead } from "./generated/ChatThreadRead";
import type { CaseNarrativeDocumentSource as DocumentSource } from "./generated/CaseNarrativeDocumentSource";

export type { ChatThreadRead } from "./generated/ChatThreadRead";
import type { ChatThreadDetail as ThreadDetail } from "./generated/ChatThreadDetail";
export type ChatThreadDetail = ThreadDetail & { messages: ChatMessageRead[] };
export type { ChatMessageAccepted } from "./generated/ChatMessageAccepted";
export type CaseNarrativeDocumentSource = Required<DocumentSource>;
export type { CaseNarrativeDocumentPageSpan } from "./generated/CaseNarrativeDocumentPageSpan";
export type PersistedChatMessage = ChatMessageRead;
export type ChatRun = ChatRunRead;
export type ThreadStatus = ThreadRead["status"];
export type RunStatus = ChatRunRead["status"];
export type ChatMessageAction = NonNullable<ChatMessageCreate["action"]>;
export type DocumentExtractionMethod = DocumentSource["extraction_method"];
export type DocumentVerificationStatus = DocumentSource["verification_status"];
export type DocumentConfidenceStatus = DocumentSource["confidence_status"];

export interface CaseIntakeSubmission {
  title?: string;
  description: string;
  documentSources?: CaseNarrativeDocumentSource[];
}

export type ChatReportSupportType =
  | "user_reported"
  | "analytical_inference"
  | "general_technical_knowledge"
  | "mitre_mapping_candidate"
  | "unknown";

export interface ChatReportClaim {
  claim_id: string;
  section_id: string;
  text: string;
  support_type: ChatReportSupportType;
  source_message_ids: string[];
  mitre_technique_ids: string[];
}

export interface ChatReportSection {
  section_id: string;
  heading: string;
  paragraphs: string[];
  items: string[];
}

export interface ChatStructuredReport {
  report_version: "preliminary_analysis_report_v1";
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
  analysis_message_id: string;
  retrieval_context_id: string | null;
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
