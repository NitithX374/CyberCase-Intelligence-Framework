import { caseUrl, getBlob, http, LONG_REQUEST_TIMEOUT_MS } from "@/lib/api/http";
import type { CaseReportCreate, CaseReportRead } from "@/lib/api/types";

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
