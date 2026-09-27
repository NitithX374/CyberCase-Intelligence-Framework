import { caseUrl, getBlob, http, UPLOAD_REQUEST_TIMEOUT_MS } from "@/lib/api/http";
import type { CaseDocumentRead, CaseSourceCreate, CaseSourceRead } from "@/lib/api/types";

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
