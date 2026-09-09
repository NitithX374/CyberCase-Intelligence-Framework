import { accountStorageKey } from "@/lib/account-storage";
import { useEffect, useSyncExternalStore } from "react";
import {
  generateOcrIdempotencyKey,
  type DocumentIngestionMode,
  type IngestedDocumentPreview,
} from "@/lib/document-ingestion";

const STORAGE_KEY_PREFIX = "cybercase_document_ingestion_preview_v2";

export interface DocumentIngestionState {
  file: File | null;
  fileName: string | null;
  fileSize: number | null;
  mode: DocumentIngestionMode;
  isProcessing: boolean;
  result: IngestedDocumentPreview | null;
  error: string | null;
  idempotencyKey: string | null;
}

export const DEFAULT_STATE: DocumentIngestionState = {
  file: null,
  fileName: null,
  fileSize: null,
  mode: "unified",
  isProcessing: false,
  result: null,
  error: null,
  idempotencyKey: null,
};

function getStorageKey(caseKey: string): string {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  return accountStorageKey(`${STORAGE_KEY_PREFIX}:${normalizedKey}`);
}

function loadInitialState(caseKey: string): DocumentIngestionState {
  if (typeof window === "undefined" || typeof window.localStorage === "undefined") {
    return DEFAULT_STATE;
  }

  try {
    const raw = window.localStorage.getItem(getStorageKey(caseKey));
    if (!raw) return DEFAULT_STATE;
    const parsed = JSON.parse(raw);
    return {
      file: null,
      fileName: typeof parsed.fileName === "string" ? parsed.fileName : null,
      fileSize: typeof parsed.fileSize === "number" ? parsed.fileSize : null,
      mode: parsed.mode === "routed" ? "routed" : "unified",
      isProcessing: false,
      result: parsed.result ?? null,
      error: typeof parsed.error === "string" ? parsed.error : null,
      idempotencyKey:
        typeof parsed.idempotencyKey === "string" ? parsed.idempotencyKey : null,
    };
  } catch (error) {
    throw new Error("Unable to restore saved document preparation", { cause: error });
  }
}

function saveToLocalStorage(caseKey: string, state: DocumentIngestionState) {
  if (typeof window === "undefined" || typeof window.localStorage === "undefined") {
    return;
  }
  try {
    const key = getStorageKey(caseKey);
    if (!state.result && !state.fileName && !state.error && state.mode === "unified") {
      window.localStorage.removeItem(key);
    } else {
      window.localStorage.setItem(
        key,
        JSON.stringify({
          fileName: state.fileName ?? state.file?.name ?? null,
          fileSize: state.fileSize ?? state.file?.size ?? null,
          mode: state.mode,
          result: state.result,
          error: state.error,
          idempotencyKey: state.idempotencyKey,
        }),
      );
    }
  } catch (error) {
    throw new Error("Unable to save document preparation in this browser", { cause: error });
  }
}

const caseStates = new Map<string, DocumentIngestionState>();
const hydratedCases = new Set<string>();
const listeners = new Set<() => void>();

function notify(caseKey: string) {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  const state = caseStates.get(getStorageKey(normalizedKey)) ?? DEFAULT_STATE;
  saveToLocalStorage(normalizedKey, state);
  listeners.forEach((listener) => listener());
}

export function getDocumentIngestionSnapshot(caseKey: string = "draft"): DocumentIngestionState {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  return caseStates.get(getStorageKey(normalizedKey)) ?? DEFAULT_STATE;
}

export function getServerSnapshot(): DocumentIngestionState {
  return DEFAULT_STATE;
}

export function subscribeDocumentIngestion(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function hydrateDocumentIngestionStore(caseKey: string = "draft") {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  if (hydratedCases.has(getStorageKey(normalizedKey))) return;
  hydratedCases.add(getStorageKey(normalizedKey));
  const restored = loadInitialState(normalizedKey);
  if (
    restored.fileName ||
    restored.result ||
    restored.error ||
    restored.mode !== "unified" ||
    restored.idempotencyKey
  ) {
    caseStates.set(getStorageKey(normalizedKey), restored);
    listeners.forEach((listener) => listener());
  }
}

export function setDocumentIngestionFile(file: File | null, caseKey: string = "draft") {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  hydratedCases.add(getStorageKey(normalizedKey));
  const prev = caseStates.get(getStorageKey(normalizedKey)) ?? DEFAULT_STATE;
  const idempotencyKey = file
    ? generateOcrIdempotencyKey(normalizedKey, file, prev.mode)
    : null;

  caseStates.set(getStorageKey(normalizedKey), {
    ...prev,
    file,
    fileName: file ? file.name : null,
    fileSize: file ? file.size : null,
    result: null,
    error: null,
    idempotencyKey,
  });
  notify(normalizedKey);
}

export function setDocumentIngestionMode(
  mode: DocumentIngestionMode,
  caseKey: string = "draft",
) {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  const prev = caseStates.get(getStorageKey(normalizedKey)) ?? DEFAULT_STATE;
  const idempotencyKey = prev.file
    ? generateOcrIdempotencyKey(normalizedKey, prev.file, mode)
    : prev.idempotencyKey;

  caseStates.set(getStorageKey(normalizedKey), {
    ...prev,
    mode,
    idempotencyKey,
  });
  notify(normalizedKey);
}

export function setDocumentIngestionProcessing(
  isProcessing: boolean,
  caseKey: string = "draft",
) {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  const prev = caseStates.get(getStorageKey(normalizedKey)) ?? DEFAULT_STATE;
  caseStates.set(getStorageKey(normalizedKey), {
    ...prev,
    isProcessing,
  });
  notify(normalizedKey);
}

export function setDocumentIngestionResult(
  result: IngestedDocumentPreview | null,
  caseKey: string = "draft",
) {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  const prev = caseStates.get(getStorageKey(normalizedKey)) ?? DEFAULT_STATE;
  caseStates.set(getStorageKey(normalizedKey), {
    ...prev,
    result,
    error: null,
  });
  notify(normalizedKey);
}

export function setDocumentIngestionError(
  error: string | null,
  caseKey: string = "draft",
) {
  const normalizedKey = (caseKey || "draft").trim() || "draft";
  const prev = caseStates.get(getStorageKey(normalizedKey)) ?? DEFAULT_STATE;
  caseStates.set(getStorageKey(normalizedKey), {
    ...prev,
    error,
  });
  notify(normalizedKey);
}

export function resetDocumentIngestionState(caseKey?: string) {
  if (caseKey) {
    const normalizedKey = (caseKey || "draft").trim() || "draft";
    caseStates.delete(getStorageKey(normalizedKey));
    hydratedCases.delete(getStorageKey(normalizedKey));
    if (typeof window !== "undefined" && window.localStorage) {
      try {
        window.localStorage.removeItem(getStorageKey(normalizedKey));
      } catch (error) {
        throw new Error("Unable to clear saved document preparation", { cause: error });
      }
    }
    notify(normalizedKey);
  } else {
    caseStates.clear();
    hydratedCases.clear();
    if (typeof window !== "undefined" && window.localStorage) {
      try {
        const keysToRemove: string[] = [];
        for (let i = 0; i < window.localStorage.length; i++) {
          const key = window.localStorage.key(i);
          if (
            key &&
            (key.startsWith(accountStorageKey(STORAGE_KEY_PREFIX)) ||
              key.startsWith("cybercase_document_ingestion_preview_v1"))
          ) {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach((k) => window.localStorage.removeItem(k));
      } catch (error) {
        throw new Error("Unable to clear saved document preparation", { cause: error });
      }
    }
    listeners.forEach((listener) => listener());
  }
}

export function useDocumentIngestion(caseKey: string = "draft") {
  const normalizedKey = (caseKey || "draft").trim() || "draft";

  useEffect(() => {
    hydrateDocumentIngestionStore(normalizedKey);
  }, [normalizedKey]);

  const state = useSyncExternalStore(
    subscribeDocumentIngestion,
    () => getDocumentIngestionSnapshot(normalizedKey),
    getServerSnapshot,
  );

  return {
    ...state,
    caseKey: normalizedKey,
    setFile: (file: File | null) => setDocumentIngestionFile(file, normalizedKey),
    setMode: (mode: DocumentIngestionMode) => setDocumentIngestionMode(mode, normalizedKey),
    setIsProcessing: (isProcessing: boolean) =>
      setDocumentIngestionProcessing(isProcessing, normalizedKey),
    setResult: (result: IngestedDocumentPreview | null) =>
      setDocumentIngestionResult(result, normalizedKey),
    setError: (error: string | null) => setDocumentIngestionError(error, normalizedKey),
    reset: () => resetDocumentIngestionState(normalizedKey),
  };
}
