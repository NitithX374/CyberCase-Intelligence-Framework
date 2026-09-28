import axios from "axios";

export const LONG_REQUEST_TIMEOUT_MS = 120_000;
export const UPLOAD_REQUEST_TIMEOUT_MS = 15 * 60_000;

export const http = axios.create({ withCredentials: true, timeout: 15_000 });

http.interceptors.request.use((config) => {
  config.baseURL = apiBaseUrl();
  return config;
});

export function apiBaseUrl(): string {
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

export function caseUrl(caseId: string, ...parts: string[]): string {
  return `/${["cases", caseId, ...parts].map(encodeURIComponent).join("/")}`;
}

export async function getBlob(url: string, signal?: AbortSignal): Promise<Blob> {
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
