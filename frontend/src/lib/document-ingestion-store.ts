import { useSyncExternalStore } from "react";
import type {
  DocumentIngestionMode,
  IngestedDocumentPreview,
} from "@/lib/document-ingestion";

const STORAGE_KEY = "cybercase_document_ingestion_preview_v1";

export interface DocumentIngestionState {
  file: File | null;
  fileName: string | null;
  fileSize: number | null;
  mode: DocumentIngestionMode;
  isProcessing: boolean;
  result: IngestedDocumentPreview | null;
  error: string | null;
}

function loadInitialState(): DocumentIngestionState {
  const defaultState: DocumentIngestionState = {
    file: null,
    fileName: null,
    fileSize: null,
    mode: "unified",
    isProcessing: false,
    result: null,
    error: null,
  };

  if (typeof window === "undefined" || typeof window.sessionStorage === "undefined") {
    return defaultState;
  }

  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultState;
    const parsed = JSON.parse(raw);
    return {
      file: null, // Binary File cannot be serialized, but metadata & result are preserved
      fileName: typeof parsed.fileName === "string" ? parsed.fileName : null,
      fileSize: typeof parsed.fileSize === "number" ? parsed.fileSize : null,
      mode: parsed.mode === "routed" ? "routed" : "unified",
      isProcessing: false,
      result: parsed.result ?? null,
      error: typeof parsed.error === "string" ? parsed.error : null,
    };
  } catch {
    return defaultState;
  }
}

function saveToSessionStorage(state: DocumentIngestionState) {
  if (typeof window === "undefined" || typeof window.sessionStorage === "undefined") {
    return;
  }
  try {
    if (!state.result && !state.fileName && !state.error && state.mode === "unified") {
      window.sessionStorage.removeItem(STORAGE_KEY);
    } else {
      window.sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          fileName: state.fileName ?? state.file?.name ?? null,
          fileSize: state.fileSize ?? state.file?.size ?? null,
          mode: state.mode,
          result: state.result,
          error: state.error,
        }),
      );
    }
  } catch {
    // Ignore storage quota or disabled errors
  }
}

let currentState: DocumentIngestionState = loadInitialState();
const listeners = new Set<() => void>();

function notify() {
  saveToSessionStorage(currentState);
  listeners.forEach((listener) => listener());
}

export function getDocumentIngestionSnapshot(): DocumentIngestionState {
  return currentState;
}

export function subscribeDocumentIngestion(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function setDocumentIngestionFile(file: File | null) {
  currentState = {
    ...currentState,
    file,
    fileName: file ? file.name : null,
    fileSize: file ? file.size : null,
    result: null,
    error: null,
  };
  notify();
}

export function setDocumentIngestionMode(mode: DocumentIngestionMode) {
  currentState = {
    ...currentState,
    mode,
  };
  notify();
}

export function setDocumentIngestionProcessing(isProcessing: boolean) {
  currentState = {
    ...currentState,
    isProcessing,
  };
  notify();
}

export function setDocumentIngestionResult(result: IngestedDocumentPreview | null) {
  currentState = {
    ...currentState,
    result,
    error: null,
  };
  notify();
}

export function setDocumentIngestionError(error: string | null) {
  currentState = {
    ...currentState,
    error,
  };
  notify();
}

export function resetDocumentIngestionState() {
  currentState = {
    file: null,
    fileName: null,
    fileSize: null,
    mode: "unified",
    isProcessing: false,
    result: null,
    error: null,
  };
  notify();
}

export function useDocumentIngestion() {
  const state = useSyncExternalStore(
    subscribeDocumentIngestion,
    getDocumentIngestionSnapshot,
    getDocumentIngestionSnapshot,
  );

  return {
    ...state,
    setFile: setDocumentIngestionFile,
    setMode: setDocumentIngestionMode,
    setIsProcessing: setDocumentIngestionProcessing,
    setResult: setDocumentIngestionResult,
    setError: setDocumentIngestionError,
    reset: resetDocumentIngestionState,
  };
}
