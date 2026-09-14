import type {
  ChatMessageRead,
  ChatRetryRequest,
  ChatThreadDetail as GeneratedChatThreadDetail,
  ChatThreadRead,
} from "./generated/chatTypes";

export type CaseRead = import("./generated/caseTypes").CaseRead;
export type PersistedChatMessage = ChatMessageRead;
export type ChatThreadDetail = Omit<
  GeneratedChatThreadDetail,
  "messages" | "retry_request"
> & {
  messages: PersistedChatMessage[];
  retry_request: ChatRetryRequest | null;
};
export type ThreadStatus = ChatThreadRead["status"];
export type ChatMessageAction = "ask" | "add_case_info";

export interface CaseIntakeSubmission {
  title?: string;
  description: string;
}

export type { ChatThreadRead } from "./generated/chatTypes";
export type {
  AdmitExtractionRequest,
  CaseAnalysisAccepted,
  CaseAnalysisCreate,
  CaseAnalysisResultRead,
  CaseChatMessageAccepted,
  CaseClarificationAccepted,
  CaseClarificationAnswer,
  CaseClarificationRead,
  CaseRunRead,
} from "./generated/runTypes";
export type {
  CaseDocumentRead,
  CaseNarrativeDocumentPageSpan,
  DocumentExtractionRead,
} from "./generated/caseTypes";
import type {
  CaseEvidenceCreate,
  EvidenceSourceRead,
} from "./generated/evidenceTypes";
export type {
  CaseEvidenceCreate,
  EvidenceSourceRead,
};

export type CaseEvidenceSnapshotRead = EvidenceSourceRead[] | {
  id?: string;
  case_id?: string;
  evidence_revision?: number;
  sources?: EvidenceSourceRead[];
  manifest_json?: unknown[];
  text_sha256?: string;
  manifest_sha256?: string;
  format_version?: string;
  input_text?: string;
  created_at?: string;
};
export type EvidenceRevisionRead = Record<string, unknown>;
export type { CaseReportCreate } from "./generated/reportTypes";
export type {
  CaseReport,
  CaseReportClaim,
  CaseReportSection,
  CaseStructuredReport,
} from "./case-report";

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
