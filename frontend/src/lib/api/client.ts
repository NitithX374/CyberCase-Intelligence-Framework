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
): Promise<Blob> =>
  getBlob(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/documents/${encodeURIComponent(documentId)}/content`,
    signal,
  );

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
): Promise<Blob> =>
  getBlob(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/reports/${encodeURIComponent(reportId)}/pdf`,
    signal,
  );

export const downloadCaseReportHtml = async (
  caseId: string,
  reportId: string,
  signal?: AbortSignal,
): Promise<Blob> =>
  getBlob(
    `${getApiBaseUrl()}/cases/${encodeURIComponent(caseId)}/reports/${encodeURIComponent(reportId)}/html`,
    signal,
  );

async function getBlob(url: string, signal?: AbortSignal): Promise<Blob> {
  try {
    const response = await axios.get<Blob>(url, { signal, responseType: "blob", timeout: 120_000 });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data instanceof Blob) {
      const body = error.response.data;
      if (body.type.includes("json")) {
        error.response.data = await body
          .text()
          .then((text) => JSON.parse(text) as unknown)
          .catch(() => body);
      }
    }
    throw error;
  }
}

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
