import { caseUrl, http } from "@/lib/api/http";
import { postWithProgress, type StreamedStep } from "@/lib/api/stream";
import type { CaseChatRead, CaseChatResponse } from "@/lib/api/types";

export async function getCaseChat(caseId: string, signal?: AbortSignal): Promise<CaseChatRead> {
  return (await http.get<CaseChatRead>(caseUrl(caseId, "chat"), { signal })).data;
}

export async function createCaseChatMessage(
  caseId: string,
  content: string,
  idempotencyKey: string,
  onStep: (step: StreamedStep) => void = () => undefined,
): Promise<CaseChatResponse> {
  const request = { content, client_request_id: idempotencyKey };
  return postWithProgress<CaseChatResponse>(caseUrl(caseId, "chat", "messages"), request, {
    onStep,
  });
}
