import axios from "axios";
import type {
  CaseAnalysisCreate,
  AnalysisStepRead,
  CaseAnalysisResultRead,
  CaseChatResponse,
  CaseChatDetail,
  CaseChatRead,
  CaseDocumentRead,
  CaseRead,
  CaseReport,
  CaseReportCreate,
  CaseSourceCreate,
  CaseSourceRead,
  UserProfile,
} from "./types";
import type { CaseReportRead } from "./generated/reportTypes";

const CHAT_REQUEST_TIMEOUT_MS = 15_000;
const DEFAULT_REQUEST_TIMEOUT_MS = 15_000;
const ANALYSIS_REQUEST_TIMEOUT_MS = 300_000;

axios.defaults.withCredentials = true;
axios.defaults.timeout = DEFAULT_REQUEST_TIMEOUT_MS;

export type ResponseLanguage = "thai" | "english";

export function detectResponseLanguage(text: string): ResponseLanguage {
  if (/[\u0e00-\u0e7f]/u.test(text)) return "thai";
  return "english";
}

export function getApiBaseUrl(): string {
  let url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) {
    if (typeof window !== "undefined") {
      throw new Error("NEXT_PUBLIC_API_URL is not set. The application cannot start.");
    }
    return "http://build-time-placeholder";
  }

  if (!url.startsWith("http")) {
    url = `https://${url}`;
  }

  if (!url.endsWith("/api/v1") && !url.endsWith("/api/v1/")) {
    url = url.endsWith("/") ? `${url}api/v1` : `${url}/api/v1`;
  }

  return url;
}

export const getCaseChat = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseChatDetail> => {
  const response = await axios.get<CaseChatRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/chat`,
    { signal, timeout: CHAT_REQUEST_TIMEOUT_MS },
  );
  return { ...response.data, messages: response.data.messages ?? [] };
};

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (typeof data === "string" && data.trim()) return data.trim();
    if (data && typeof data === "object" && "detail" in data) {
      const detail = (data as { detail?: unknown }).detail;
      if (typeof detail === "string" && detail.trim()) return detail.trim();
      if (
        detail &&
        typeof detail === "object" &&
        "message" in detail &&
        typeof detail.message === "string"
      ) {
        return detail.message.trim();
      }
      if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0];
        if (typeof first === "string" && first.trim()) return first.trim();
        if (first && typeof first === "object" && "msg" in first && typeof first.msg === "string") {
          return first.msg.trim();
        }
      }
    }
  }
  if (error instanceof Error && error.message.trim()) {
    return error.message.trim();
  }
  return fallback;
}

export const getSession = async (signal?: AbortSignal): Promise<UserProfile | null> => {
  const response = await axios.get<UserProfile | null>(`${getApiBaseUrl()}/auth/session`, {
    signal,
    timeout: CHAT_REQUEST_TIMEOUT_MS,
  });
  return response.data;
};

export const logout = async (signal?: AbortSignal): Promise<{ message: string }> => {
  const response = await axios.post<{ message: string }>(
    `${getApiBaseUrl()}/auth/logout`,
    {},
    { signal },
  );
  return response.data;
};

export const createCaseChatMessage = async (
  caseId: string,
  content: string,
  idempotencyKey: string,
): Promise<CaseChatResponse> => {
  const response = await axios.post<CaseChatResponse>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/chat/messages`,
    {
      content,
      client_request_id: idempotencyKey,
      response_language: detectResponseLanguage(content),
    },
    { timeout: ANALYSIS_REQUEST_TIMEOUT_MS },
  );
  return response.data;
};

export const listCases = async (signal?: AbortSignal): Promise<CaseRead[]> => {
  const response = await axios.get<CaseRead[]>(`${getApiBaseUrl()}/cases`, { signal });
  return response.data;
};

export const createCase = async (
  title: string = "New case",
  signal?: AbortSignal,
): Promise<CaseRead> => {
  const response = await axios.post<CaseRead>(`${getApiBaseUrl()}/cases`, { title }, { signal });
  return response.data;
};

export const getCase = async (caseId: string, signal?: AbortSignal): Promise<CaseRead> => {
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

export const deleteCase = async (caseId: string, signal?: AbortSignal): Promise<void> => {
  await axios.delete(`${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}`, { signal });
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

export const fetchCaseDocumentContent = async (
  caseId: string,
  documentId: string,
  signal?: AbortSignal,
): Promise<Blob> => {
  const response = await axios.get<Blob>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/documents/${encodeURIComponent(documentId)}/content`,
    { signal, responseType: "blob", timeout: 120_000 },
  );
  return response.data;
};

export const listCaseSources = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseSourceRead[]> => {
  const response = await axios.get<CaseSourceRead[]>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/sources`,
    { signal },
  );
  return response.data;
};

export const addCaseSource = async (
  caseId: string,
  request: CaseSourceCreate,
  signal?: AbortSignal,
): Promise<CaseSourceRead> => {
  const response = await axios.post<CaseSourceRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/sources`,
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

export const startCaseAnalysis = async (
  caseId: string,
  request: CaseAnalysisCreate,
  signal?: AbortSignal,
): Promise<AnalysisStepRead> => {
  const response = await axios.post<AnalysisStepRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/analysis`,
    request,
    { signal, timeout: ANALYSIS_REQUEST_TIMEOUT_MS },
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

export const listCaseReports = async (
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseReport[]> => {
  const response = await axios.get<CaseReportRead[]>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/reports`,
    { signal },
  );
  return response.data.map(normalizeCaseReport);
};

export const generateCaseReport = async (
  caseId: string,
  request: CaseReportCreate,
  signal?: AbortSignal,
): Promise<CaseReport> => {
  const response = await axios.post<CaseReportRead>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/reports`,
    request,
    { signal, timeout: 120_000 },
  );
  return normalizeCaseReport(response.data);
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

export const downloadCaseReportHtml = async (
  caseId: string,
  reportId: string,
  signal?: AbortSignal,
): Promise<Blob> => {
  const response = await axios.get<Blob>(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/reports/${encodeURIComponent(reportId)}/html`,
    { signal, responseType: "blob", timeout: 120_000 },
  );
  return response.data;
};

function normalizeCaseReport(report: CaseReportRead): CaseReport {
  return {
    ...report,
    report: {
      ...report.report,
      sections: report.report.sections.map((section) => ({
        ...section,
        paragraphs: section.paragraphs ?? [],
        items: section.items ?? [],
      })),
      claims: (report.report.claims ?? []).map((claim) => ({
        ...claim,
        source_ids: claim.source_ids ?? [],
        mitre_technique_ids: claim.mitre_technique_ids ?? [],
      })),
      limitations: report.report.limitations ?? [],
    },
  };
}
