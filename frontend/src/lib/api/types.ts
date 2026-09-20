import type { CaseChatRead, ChatMessageRead } from "./generated/chatTypes";
import type {
  CaseReportRead,
  ReportClaim,
  ReportSection,
  StructuredReport,
} from "./generated/reportTypes";

export type CaseRead = import("./generated/caseTypes").CaseRead;
export type { ChatMessageRead } from "./generated/chatTypes";
export type CaseChatDetail = Omit<CaseChatRead, "messages"> & {
  messages: ChatMessageRead[];
};
export type CaseChatStatus = CaseChatRead["status"];

export type { CaseChatRead } from "./generated/chatTypes";
export type {
  AnalysisStepRead,
  CaseAnalysisClaim,
  CaseAnalysisCreate,
  CaseAnalysisGap,
  CaseAnalysisResultRead,
  CaseAnalysisTrace,
  CaseChatResponse,
  CaseGroundingReport,
  CaseImpactItem,
  CaseInvolvedParty,
  CaseMitreAssociation,
  CaseSourceCitation,
  CaseTimelineItem,
  FollowupQuestionRead,
} from "./generated/analysisTypes";
export type { CaseDocumentRead, DocumentExtractionRead } from "./generated/caseTypes";
export type { CaseSourceCreate, CaseSourceRead } from "./generated/sourceTypes";
export type { CaseReportCreate } from "./generated/reportTypes";
export type CaseReportClaim = Omit<ReportClaim, "source_ids" | "mitre_technique_ids"> & {
  source_ids: string[];
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
  report: CaseStructuredReport;
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
