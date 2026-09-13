import axios from "axios";
import type {
  AuthTokenResponse,
  ChatThreadDetail,
  DevLoginPayload,
  UserProfile,
} from "./apiTypes";
import { normalizeChatThreadDetail } from "./chat-api-adapter";
import type { ChatThreadDetail as ChatThreadDetailWire } from "./generated/chatTypes";

axios.defaults.withCredentials = true;

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
    url = `https://${url}`;
  }

  if (!url.endsWith("/api/v1") && !url.endsWith("/api/v1/")) {
    url = url.endsWith("/") ? `${url}api/v1` : `${url}/api/v1`;
  }

  return url;
}

export const getChatThread = async (
  threadId: string,
  signal?: AbortSignal,
): Promise<ChatThreadDetail> => {
  const response = await axios.get<ChatThreadDetailWire>(
    `${getApiBaseUrl()}/chats/${encodeURIComponent(threadId)}`,
    { signal, timeout: CHAT_POLL_REQUEST_TIMEOUT_MS },
  );
  return normalizeChatThreadDetail(response.data);
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

export const getSession = async (
  signal?: AbortSignal,
): Promise<UserProfile | null> => {
  const response = await axios.get<UserProfile | null>(
    `${getApiBaseUrl()}/auth/session`,
    { signal },
  );
  return response.data;
};

export const devLogin = async (
  payload: DevLoginPayload,
  signal?: AbortSignal,
): Promise<AuthTokenResponse> => {
  const response = await axios.post<AuthTokenResponse>(
    `${getApiBaseUrl()}/auth/dev-login`,
    payload,
    { signal },
  );
  return response.data;
};

export const logout = async (
  signal?: AbortSignal,
): Promise<{ message: string }> => {
  const response = await axios.post<{ message: string }>(
    `${getApiBaseUrl()}/auth/logout`,
    {},
    { signal },
  );
  return response.data;
};

export const getOAuthLoginUrl = (
  provider: "google" = "google",
  redirect?: string,
): string => {
  const base = `${getApiBaseUrl()}/auth/login/${provider}`;
  return redirect ? `${base}?redirect=${encodeURIComponent(redirect)}` : base;
};
