import axios from "axios";
import type {
  AnalysisStepRead,
  CaseAnalysisResultRead,
  CaseChatRead,
  CaseChatResponse,
  CaseDocumentRead,
  CaseRead,
  CaseReportCreate,
  CaseReportRead,
  CaseSourceCreate,
  CaseSourceRead,
  PasswordLoginRequest,
  RegisterRequest,
  UserRead,
} from "./types";

const LONG_REQUEST_TIMEOUT_MS = 120_000;
const UPLOAD_REQUEST_TIMEOUT_MS = 15 * 60_000;
const ANALYSIS_REQUEST_TIMEOUT_MS = 20 * 60_000;

export const http = axios.create({ withCredentials: true, timeout: 15_000 });

http.interceptors.request.use((config) => {
  config.baseURL = getApiBaseUrl();
  return config;
});

function getApiBaseUrl(): string {
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

function caseUrl(caseId: string, ...parts: string[]): string {
  return `/${["cases", caseId, ...parts].map(encodeURIComponent).join("/")}`;
}

export async function login(request: PasswordLoginRequest): Promise<UserRead> {
  return (await http.post<UserRead>("/auth/login", request)).data;
}

export async function register(request: RegisterRequest): Promise<UserRead> {
  return (await http.post<UserRead>("/auth/register", request)).data;
}

export async function getSession(signal?: AbortSignal): Promise<UserRead | null> {
  return (await http.get<UserRead | null>("/auth/session", { signal })).data;
}

export async function logout(): Promise<void> {
  await http.post("/auth/logout", {});
}

export async function listCases(signal?: AbortSignal): Promise<CaseRead[]> {
  return (await http.get<CaseRead[]>("/cases", { signal })).data;
}

export async function createCase(title = "New case"): Promise<CaseRead> {
  return (await http.post<CaseRead>("/cases", { title })).data;
}

export async function getCase(caseId: string, signal?: AbortSignal): Promise<CaseRead> {
  return (await http.get<CaseRead>(caseUrl(caseId), { signal })).data;
}

export async function updateCase(caseId: string, title: string): Promise<CaseRead> {
  return (await http.patch<CaseRead>(caseUrl(caseId), { title })).data;
}

export async function deleteCase(caseId: string): Promise<void> {
  await http.delete(caseUrl(caseId));
}

export async function getCaseChat(caseId: string, signal?: AbortSignal): Promise<CaseChatRead> {
  return (await http.get<CaseChatRead>(caseUrl(caseId, "chat"), { signal })).data;
}

export async function createCaseChatMessage(
  caseId: string,
  content: string,
  idempotencyKey: string,
): Promise<CaseChatResponse> {
  const request = { content, client_request_id: idempotencyKey };
  return (
    await http.post<CaseChatResponse>(caseUrl(caseId, "chat", "messages"), request, {
      timeout: ANALYSIS_REQUEST_TIMEOUT_MS,
    })
  ).data;
}

export async function uploadCaseDocument(caseId: string, file: File): Promise<CaseDocumentRead> {
  const body = new FormData();
  body.append("file", file);
  return (
    await http.post<CaseDocumentRead>(caseUrl(caseId, "documents"), body, {
      timeout: UPLOAD_REQUEST_TIMEOUT_MS,
    })
  ).data;
}

export function fetchCaseDocumentContent(
  caseId: string,
  documentId: string,
  signal?: AbortSignal,
): Promise<Blob> {
  return getBlob(caseUrl(caseId, "documents", documentId, "content"), signal);
}

export async function listCaseSources(
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseSourceRead[]> {
  return (await http.get<CaseSourceRead[]>(caseUrl(caseId, "sources"), { signal })).data;
}

export async function addCaseSource(
  caseId: string,
  request: CaseSourceCreate,
): Promise<CaseSourceRead> {
  return (await http.post<CaseSourceRead>(caseUrl(caseId, "sources"), request)).data;
}

export async function startCaseAnalysis(caseId: string): Promise<AnalysisStepRead> {
  return (
    await http.post<AnalysisStepRead>(
      caseUrl(caseId, "analysis"),
      {},
      { timeout: ANALYSIS_REQUEST_TIMEOUT_MS },
    )
  ).data;
}

export async function getCaseAnalysis(
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseAnalysisResultRead | null> {
  return (await http.get<CaseAnalysisResultRead | null>(caseUrl(caseId, "analysis"), { signal }))
    .data;
}

export async function listCaseReports(
  caseId: string,
  signal?: AbortSignal,
): Promise<CaseReportRead[]> {
  return (await http.get<CaseReportRead[]>(caseUrl(caseId, "reports"), { signal })).data;
}

export async function generateCaseReport(
  caseId: string,
  request: CaseReportCreate,
): Promise<CaseReportRead> {
  return (
    await http.post<CaseReportRead>(caseUrl(caseId, "reports"), request, {
      timeout: LONG_REQUEST_TIMEOUT_MS,
    })
  ).data;
}

export function downloadCaseReportPdf(caseId: string, reportId: string): Promise<Blob> {
  return getBlob(caseUrl(caseId, "reports", reportId, "pdf"));
}

export function downloadCaseReportHtml(caseId: string, reportId: string): Promise<Blob> {
  return getBlob(caseUrl(caseId, "reports", reportId, "html"));
}

async function getBlob(url: string, signal?: AbortSignal): Promise<Blob> {
  try {
    const response = await http.get<Blob>(url, {
      signal,
      responseType: "blob",
      timeout: LONG_REQUEST_TIMEOUT_MS,
    });
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
