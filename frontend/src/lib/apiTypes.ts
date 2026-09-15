import type {
  CaseChatRead,
  ChatMessageRead,
} from "./generated/chatTypes";
import type {
  CaseReportRead,
  ReportClaim,
  ReportSection,
  StructuredReport,
} from "./generated/reportTypes";

export type CaseRead = import("./generated/caseTypes").CaseRead;
export type PersistedChatMessage = ChatMessageRead;
export type CaseChatDetail = Omit<
  CaseChatRead,
  "messages"
> & {
  messages: PersistedChatMessage[];
};
export type CaseChatStatus = CaseChatRead["status"];

export interface CaseIntakeSubmission {
  title?: string;
  description: string;
}

export type { CaseChatRead } from "./generated/chatTypes";
export type {
  CaseAnalysisAccepted,
  CaseAnalysisCreate,
  CaseAnalysisResultRead,
  CaseChatMessageAccepted,
  CaseClarificationRead,
  CaseRunRead,
} from "./generated/runTypes";
export type {
  CaseDocumentRead,
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
export type { CaseReportCreate } from "./generated/reportTypes";
export type CaseReportClaim = Omit<ReportClaim, "source_evidence_ids" | "mitre_technique_ids"> & {
  source_evidence_ids: string[];
  mitre_technique_ids: string[];
};

export type CaseReportSection = Omit<ReportSection, "paragraphs" | "items"> & {
  paragraphs: string[];
  items: string[];
};

export type CaseStructuredReport = Omit<StructuredReport, "sections" | "claims" | "limitations"> & {
  sections: CaseReportSection[];
  claims: CaseReportClaim[];
  limitations: string[];
};

export type CaseReport = Omit<CaseReportRead, "report"> & {
  report: CaseStructuredReport | null;
};

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
