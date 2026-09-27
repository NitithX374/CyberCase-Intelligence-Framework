import { ANALYSIS_REQUEST_TIMEOUT_MS, caseUrl, http } from "@/lib/api/http";
import type { CaseChatRead, CaseChatResponse } from "@/lib/api/types";

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
