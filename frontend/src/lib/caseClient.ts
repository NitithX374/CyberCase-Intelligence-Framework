import axios from "axios";
import type {
  CaseAnalysisAccepted,
  CaseAnalysisCreate,
  CaseAnalysisResultRead,
  CaseClarificationAccepted,
  CaseClarificationAnswer,
  CaseClarificationRead,
  CaseDocumentRead,
  CaseEvidenceCreate,
  CaseEvidenceSnapshotRead,
  CaseRead,
  CaseReportCreate,
  CaseRunRead,
  EvidenceSourceRead,
  ChatReportRead,
  CaseChatMessageAccepted,
  CaseNarrativeDocumentSource,
  ChatMessageAction,
  ChatThreadDetail,
} from "./apiTypes";
import { getApiBaseUrl } from "./apiClient";

export const createCaseChatMessage = async (
  threadId: string,
  content: string,
  idempotencyKey: string,
  signal?: AbortSignal,
  action?: ChatMessageAction,
  documentSources?: CaseNarrativeDocumentSource[],
): Promise<CaseChatMessageAccepted> => {
  const response = await axios.post<CaseChatMessageAccepted>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(threadId)}/chat/messages`,
    {
      content,
      idempotency_key: idempotencyKey,
      ...(action ? { action } : {}),
      ...(documentSources?.length
        ? { document_sources: documentSources }
        : {}),
    },
    { signal },
  );
  return response.data;
};

export const getCaseChat = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<ChatThreadDetail> => {
  const response = await axios.get<ChatThreadDetail>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/chat`,
    { signal },
  );
  return response.data;
};

export const listCases = async (
  signal?: AbortSignal,
): Promise<CaseRead[]> => {
  const response = await axios.get<CaseRead[]>(`${getApiBaseUrl()}/cases`, {
    signal,
  });
  return response.data;
};

export const createCase = async (
  title: string = "New case",
  signal?: AbortSignal,
): Promise<CaseRead> => {
  const response = await axios.post<CaseRead>(
    `${getApiBaseUrl()}/cases`,
    { title },
    { signal },
  );
  return response.data;
};

export const getCase = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseRead> => {
  const response = await axios.get<CaseRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}`,
    { signal },
  );
  return response.data;
};

export const updateCase = async (
  caseId: string,
  title: string,
  signal?: AbortSignal,
): Promise<CaseRead> => {
  const response = await axios.patch<CaseRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}`,
    { title },
    { signal },
  );
  return response.data;
};

export const deleteCase = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<void> => {
  await axios.delete(`${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}`, {
    signal,
  });
};

export const listCaseDocuments = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseDocumentRead[]> => {
  const response = await axios.get<CaseDocumentRead[]>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/documents`,
    { signal },
  );
  return response.data;
};

export const listCaseEvidence = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<EvidenceSourceRead[]> => {
  const response = await axios.get<EvidenceSourceRead[]>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/evidence`,
    { signal },
  );
  return response.data;
};

export const admitCaseEvidence = async (
  caseId: string,
  request: CaseEvidenceCreate,
  signal?: AbortSignal,
): Promise<EvidenceSourceRead> => {
  const response = await axios.post<EvidenceSourceRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/evidence`,
    request,
    { signal },
  );
  return response.data;
};

export const uploadCaseDocument = async (
  caseId: string,
  file: File,
  signal?: AbortSignal,
): Promise<CaseDocumentRead> => {
  const body = new FormData();
  body.append("file", file);
  const response = await axios.post<CaseDocumentRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/documents`,
    body,
    { signal, timeout: 120_000 },
  );
  return response.data;
};

export const admitCaseDocument = async (
  caseId: string,
  documentId: string,
  extractionId: string,
  signal?: AbortSignal,
): Promise<EvidenceSourceRead> => {
  const response = await axios.post<EvidenceSourceRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/documents/${encodeURIComponent(documentId)}/admit`,
    { extraction_id: extractionId },
    { signal },
  );
  return response.data;
};

export const startCaseAnalysis = async (
  caseId: string,
  request: CaseAnalysisCreate,
  signal?: AbortSignal,
): Promise<CaseAnalysisAccepted> => {
  const response = await axios.post<CaseAnalysisAccepted>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/analysis`,
    request,
    { signal, timeout: 30_000 },
  );
  return response.data;
};

export const getCaseAnalysis = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseAnalysisResultRead | null> => {
  const response = await axios.get<CaseAnalysisResultRead | null>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/analysis`,
    { signal, timeout: 15_000 },
  );
  return response.data;
};

export const getCaseRun = async (
  caseId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<CaseRunRead> => {
  const response = await axios.get<CaseRunRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/runs/${encodeURIComponent(runId)}`,
    { signal, timeout: 15_000 },
  );
  return response.data;
};

export const getCaseEvidenceSnapshot = async (
  caseId: string,
  snapshotId: string,
  signal?: AbortSignal,
): Promise<CaseEvidenceSnapshotRead> => {
  const response = await axios.get<CaseEvidenceSnapshotRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/evidence/snapshots/${encodeURIComponent(snapshotId)}`,
    { signal, timeout: 15_000 },
  );
  return response.data;
};

export const ensureCaseChat = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<import("./apiTypes").ChatThreadRead> => {
  const response = await axios.post<import("./apiTypes").ChatThreadRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/chat`,
    {},
    { signal },
  );
  return response.data;
};

export const listCaseClarifications = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseClarificationRead[]> => {
  const response = await axios.get<CaseClarificationRead[]>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/clarifications`,
    { signal },
  );
  return response.data;
};

export const answerCaseClarification = async (
  caseId: string,
  clarificationId: string,
  request: CaseClarificationAnswer,
  signal?: AbortSignal,
): Promise<CaseClarificationAccepted> => {
  const response = await axios.post<CaseClarificationAccepted>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/clarifications/${encodeURIComponent(clarificationId)}/answers`,
    request,
    { signal, timeout: 30_000 },
  );
  return response.data;
};

export const listCaseReports = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<ChatReportRead[]> => {
  const response = await axios.get<ChatReportRead[]>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/reports`,
    { signal },
  );
  return response.data;
};

export const generateCaseReport = async (
  caseId: string,
  request: CaseReportCreate,
  signal?: AbortSignal,
): Promise<ChatReportRead> => {
  const response = await axios.post<ChatReportRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/reports`,
    request,
    { signal, timeout: 120_000 },
  );
  return response.data;
};

export const downloadCaseReportPdf = async (
  caseId: string,
  reportId: string,
  signal?: AbortSignal,
): Promise<Blob> => {
  const response = await axios.get<Blob>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/reports/${encodeURIComponent(reportId)}/pdf`,
    { signal, responseType: "blob", timeout: 120_000 },
  );
  return response.data;
};
