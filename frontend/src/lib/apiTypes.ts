import type {
  CaseNarrativeDocumentSource as DocumentSource,
  CaseRead as GeneratedCaseRead,
} from "./generated/caseTypes";
import type {
  ChatMessageCreate as GeneratedChatMessageCreate,
  ChatMessageRead as GeneratedChatMessageRead,
  ChatRetryRequest as GeneratedChatRetryRequest,
  ChatRunRead,
  ChatThreadDetail as GeneratedThreadDetail,
  ChatThreadRead as ThreadRead,
} from "./generated/chatTypes";
import type { CaseRunRead } from "./generated/runTypes";

export type CaseRead = Omit<GeneratedCaseRead, "evidence_revision" | "latest_analysis_result_id" | "processing_status" | "analysis_freshness"> & {
  evidence_revision?: number;
  latest_analysis_result_id?: string | null;
  processing_status?: GeneratedCaseRead["processing_status"];
  analysis_freshness?: GeneratedCaseRead["analysis_freshness"];
};
export type ChatRetryRequest = Omit<GeneratedChatRetryRequest, "response_language"> & {
  response_language?: GeneratedChatRetryRequest["response_language"];
};
export type ChatThreadDetail = Omit<GeneratedThreadDetail, "messages" | "retry_request"> & {
  messages: PersistedChatMessage[];
  retry_request?: ChatRetryRequest | null;
};
export type ChatMessageRead = GeneratedChatMessageRead;
export type ChatMessageAccepted = {
  message: PersistedChatMessage;
  run: ChatRunRead;
};
export type CaseChatMessageAccepted = {
  message: PersistedChatMessage;
  run: CaseRunRead;
};
export type CaseNarrativeDocumentSource = Required<DocumentSource>;
export type { CaseNarrativeDocumentPageSpan } from "./generated/caseTypes";
export type PersistedChatMessage = Omit<GeneratedChatMessageRead, "message_kind" | "analysis_result_id"> & {
  message_kind?: GeneratedChatMessageRead["message_kind"];
  analysis_result_id?: string | null;
};
export type ChatRun = ChatRunRead;
export type ThreadStatus = ThreadRead["status"];
export type RunStatus = ChatRunRead["status"];
export type ChatMessageCreate = Omit<GeneratedChatMessageCreate, "response_language"> & {
  response_language?: GeneratedChatMessageCreate["response_language"];
};
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
  source_evidence_ids?: string[];
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
  thread_id: string | null;
  version_number: number;
  idempotency_key: string;
  source_snapshot_hash: string;
  analysis_message_id?: string | null;
  case_id?: string | null;
  analysis_result_id?: string | null;
  evidence_snapshot_id?: string | null;
  source_reference_type?: "legacy_chat" | "case_evidence";
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
  source_snapshot?: Record<string, unknown> | null;
}

export type { ChatThreadRead } from "./generated/chatTypes";
export type { ChatCaseLinkRead } from "./generated/chatTypes";
export type { ChatRunRead } from "./generated/chatTypes";
export type {
  AdmitExtractionRequest,
  CaseAnalysisAccepted,
  CaseAnalysisCreate,
  CaseAnalysisResultRead,
  CaseClarificationAccepted,
  CaseClarificationAnswer,
  CaseClarificationRead,
  CaseRunRead,
} from "./generated/runTypes";
export type {
  CaseDocumentRead,
  DocumentExtractionRead,
} from "./generated/caseTypes";
export type {
  CaseEvidenceCreate,
  CaseEvidenceSnapshotRead,
  EvidenceRevisionRead,
  EvidenceSourceRead,
} from "./generated/evidenceTypes";
export type { CaseReportCreate } from "./generated/reportTypes";

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar_url?: string | null;
  oauth_provider: string;
  created_at: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export interface DevLoginPayload {
  email: string;
  name?: string;
  avatar_url?: string;
}
