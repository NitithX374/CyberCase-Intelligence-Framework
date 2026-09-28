import {
  AxiosError,
  AxiosHeaders,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";
import { apiBaseUrl } from "./http";

export const STREAM_IDLE_TIMEOUT_MS = 60_000;

export interface StreamedStep {
  step: string;
  elapsed: number;
}

interface StreamOptions {
  onStep: (step: StreamedStep) => void;
  idleTimeoutMs?: number;
}

export async function postWithProgress<T>(
  path: string,
  body: unknown,
  { onStep, idleTimeoutMs = STREAM_IDLE_TIMEOUT_MS }: StreamOptions,
): Promise<T> {
  const config = {
    url: path,
    method: "post",
    headers: new AxiosHeaders(),
  } as InternalAxiosRequestConfig;
  const controller = new AbortController();
  let idle: ReturnType<typeof setTimeout> | undefined;
  let wentQuiet = false;
  const heardFrom = () => {
    clearTimeout(idle);
    idle = setTimeout(() => {
      wentQuiet = true;
      controller.abort();
    }, idleTimeoutMs);
  };
  const lost = (error: unknown) =>
    wentQuiet
      ? new AxiosError("The server went quiet for too long", AxiosError.ECONNABORTED, config)
      : new AxiosError(
          error instanceof Error ? error.message : "Network Error",
          AxiosError.ERR_NETWORK,
          config,
        );

  heardFrom();
  try {
    let response: Response;
    try {
      response = await fetch(`${apiBaseUrl()}${path}`, {
        method: "POST",
        credentials: "include",
        headers: { Accept: "text/event-stream", "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
    } catch (error) {
      throw lost(error);
    }
    if (!response.ok || !response.body) {
      throw refused(response.status, await response.json().catch(() => null), config);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffered = "";
    for (;;) {
      let chunk: ReadableStreamReadResult<Uint8Array>;
      try {
        chunk = await reader.read();
      } catch (error) {
        throw lost(error);
      }
      if (chunk.done) break;
      heardFrom();
      buffered += decoder.decode(chunk.value, { stream: true }).replace(/\r\n/g, "\n");
      for (let end = buffered.indexOf("\n\n"); end >= 0; end = buffered.indexOf("\n\n")) {
        const event = parseEvent(buffered.slice(0, end));
        buffered = buffered.slice(end + 2);
        if (event?.name === "step") onStep(JSON.parse(event.data) as StreamedStep);
        if (event?.name === "result") {
          void reader.cancel().catch(() => undefined);
          return JSON.parse(event.data) as T;
        }
        if (event?.name === "error") {
          const { status, detail } = JSON.parse(event.data) as { status: number; detail: unknown };
          throw refused(status, { detail }, config);
        }
      }
    }
    throw new AxiosError("The response ended before its result", AxiosError.ERR_NETWORK, config);
  } finally {
    clearTimeout(idle);
  }
}

function parseEvent(block: string): { name: string; data: string } | null {
  let name = "message";
  const data: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) name = line.slice("event:".length).trim();
    else if (line.startsWith("data:")) data.push(line.slice("data:".length).trimStart());
  }
  return data.length > 0 ? { name, data: data.join("\n") } : null;
}

function refused(status: number, data: unknown, config: InternalAxiosRequestConfig): AxiosError {
  const response: AxiosResponse = { status, statusText: "", headers: {}, config, data };
  return new AxiosError(
    `Request failed with status code ${status}`,
    status >= 500 ? AxiosError.ERR_BAD_RESPONSE : AxiosError.ERR_BAD_REQUEST,
    config,
    null,
    response,
  );
}
