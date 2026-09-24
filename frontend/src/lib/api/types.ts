import type { components } from "./generated/openapi";

type Schemas = components["schemas"];

export type AnalysisStepRead = Schemas["AnalysisStepRead"];
export type CaseAnalysisClaim = Schemas["CaseAnalysisClaim"];
export type CaseAnalysisCreate = Schemas["CaseAnalysisCreate"];
export type CaseAnalysisGap = Schemas["CaseAnalysisGap"];
export type CaseAnalysisResultRead = Schemas["CaseAnalysisResultRead"];
export type CaseAnalysisTrace = Schemas["CaseAnalysisTrace"];
export type CaseChatRead = Schemas["CaseChatRead"];
export type CaseChatResponse = Schemas["CaseChatResponse"];
export type CaseDocumentRead = Schemas["CaseDocumentRead"];
export type CaseMitreAssociation = Schemas["CaseMitreAssociation"];
export type CaseRead = Schemas["CaseRead"];
export type CaseReportCreate = Schemas["CaseReportCreate"];
export type CaseReportRead = Schemas["CaseReportRead"];
export type CaseSourceCitation = Schemas["CaseSourceCitation"];
export type CaseSourceCreate = Schemas["CaseSourceCreate"];
export type CaseSourceRead = Schemas["CaseSourceRead"];
export type ChatMessageRead = Schemas["ChatMessageRead"];
export type PasswordLoginRequest = Schemas["PasswordLoginRequest"];
export type RegisterRequest = Schemas["RegisterRequest"];
export type UserRead = Schemas["UserRead"];
