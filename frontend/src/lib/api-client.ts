import axios from "axios";

import type {
  ChatMessageAccepted,
  ChatMessageAction,
  ChatReportRead,
  ChatRun,
  ChatThreadDetail,
  ChatThreadRead,
} from "./api-types";

const CHAT_POLL_REQUEST_TIMEOUT_MS = 15_000;

export function getApiBaseUrl(): string {
  let url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) {
    if (typeof window !== "undefined") {
      throw new Error(
        "NEXT_PUBLIC_API_URL is not set. The application cannot start.",
      );
    }
    return "http://build-time-placeholder";
  }

  if (!url.startsWith("http")) {
    url = "https://" + url;
  }

  if (!url.endsWith("/api/v1") && !url.endsWith("/api/v1/")) {
    url = url.endsWith("/") ? url + "api/v1" : url + "/api/v1";
  }

  return url;
}

export const listChatThreads = async (
  signal?: AbortSignal,
): Promise<ChatThreadRead[]> => {
  const response = await axios.get<ChatThreadRead[]>(`${getApiBaseUrl()}/chats`, {
    signal,
  });
  return response.data;
};

export const createChatThread = async (
  title: string = "New case",
  signal?: AbortSignal,
): Promise<ChatThreadRead> => {
  const response = await axios.post<ChatThreadRead>(
    `${getApiBaseUrl()}/chats`,
    { title },
    { signal },
  );
  return response.data;
};

export const getChatThread = async (
  threadId: string,
  signal?: AbortSignal,
): Promise<ChatThreadDetail> => {
  const response = await axios.get<ChatThreadDetail>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}`,
    { signal, timeout: CHAT_POLL_REQUEST_TIMEOUT_MS },
  );
  return response.data;
};

export const updateChatThread = async (
  threadId: string,
  title: string,
  signal?: AbortSignal,
): Promise<ChatThreadRead> => {
  const response = await axios.patch<ChatThreadRead>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}`,
    { title },
    { signal },
  );
  return response.data;
};

export const deleteChatThread = async (
  threadId: string,
  signal?: AbortSignal,
): Promise<void> => {
  await axios.delete(`${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}`, {
    signal,
  });
};

export const createChatMessage = async (
  threadId: string,
  content: string,
  idempotencyKey: string,
  signal?: AbortSignal,
  action?: ChatMessageAction,
): Promise<ChatMessageAccepted> => {
  const response = await axios.post<ChatMessageAccepted>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}/messages`,
    {
      content,
      idempotency_key: idempotencyKey,
      ...(action ? { action } : {}),
    },
    { signal },
  );
  return response.data;
};

export const getChatRun = async (
  threadId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<ChatRun> => {
  const response = await axios.get<ChatRun>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}/runs/${encodeURIComponent(runId)}`,
    { signal, timeout: CHAT_POLL_REQUEST_TIMEOUT_MS },
  );
  return response.data;
};

export const listChatReports = async (
  threadId: string,
  signal?: AbortSignal,
): Promise<ChatReportRead[]> => {
  const response = await axios.get<ChatReportRead[]>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}/reports`,
    { signal },
  );
  return response.data;
};

export const getChatReport = async (
  threadId: string,
  reportId: string,
  signal?: AbortSignal,
): Promise<ChatReportRead> => {
  const response = await axios.get<ChatReportRead>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}/reports/${encodeURIComponent(reportId)}`,
    { signal },
  );
  return response.data;
};

export const downloadChatReportPdf = async (
  threadId: string,
  reportId: string,
  signal?: AbortSignal,
): Promise<Blob> => {
  const response = await axios.get<Blob>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}/reports/${encodeURIComponent(reportId)}/pdf`,
    { signal, responseType: "blob", timeout: 120_000 },
  );
  return response.data;
};

export const generateChatReport = async (
  threadId: string,
  idempotencyKey?: string,
  signal?: AbortSignal,
): Promise<ChatReportRead> => {
  const response = await axios.post<ChatReportRead>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}/reports`,
    idempotencyKey ? { idempotency_key: idempotencyKey } : {},
    { signal, timeout: 120_000 },
  );
  return response.data;
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
        if (
          first &&
          typeof first === "object" &&
          "msg" in first &&
          typeof first.msg === "string"
        ) {
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
