import { AxiosError, AxiosHeaders } from "axios";

function responseError(status: number, data: unknown): AxiosError {
  const config = { headers: new AxiosHeaders() };
  return new AxiosError(
    `Request failed with status code ${status}`,
    status >= 500 ? "ERR_BAD_RESPONSE" : "ERR_BAD_REQUEST",
    config,
    undefined,
    { status, statusText: "", headers: {}, config, data },
  );
}

export function httpError(status: number, detail: unknown): AxiosError {
  return responseError(status, { detail });
}

export function refusal(status: number, code: string, message: string): AxiosError {
  return httpError(status, { code, message });
}

export function blobRefusal(status: number, code: string, message: string): AxiosError {
  const body = JSON.stringify({ detail: { code, message } });
  return responseError(status, new Blob([body], { type: "application/json" }));
}

export function timeoutError(): AxiosError {
  return new AxiosError("timeout of 15000ms exceeded", "ECONNABORTED");
}

export function networkError(): AxiosError {
  return new AxiosError("Network Error", "ERR_NETWORK");
}
