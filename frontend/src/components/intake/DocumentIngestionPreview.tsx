"use client";

import { useRef } from "react";
import { Icon } from "@/components/common/icons";
import { getApiErrorMessage } from "@/lib/api";
import {
  previewDocumentIngestion,
  type DocumentIngestionMode,
} from "@/lib/document-ingestion";
import { useDocumentIngestion } from "@/lib/document-ingestion-store";
import { DocumentIngestionResult } from "./DocumentIngestionResult";

const ACCEPTED_TYPES = ".pdf,.docx,.png,.jpg,.jpeg";

export function DocumentIngestionPreview() {
  const {
    file,
    fileName,
    mode,
    isProcessing,
    result,
    error,
    setFile,
    setMode,
    setIsProcessing,
    setResult,
    setError,
    reset,
  } = useDocumentIngestion();

  const fileInputRef = useRef<HTMLInputElement>(null);

  const processDocument = async () => {
    if (!file || isProcessing) return;
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      setResult(await previewDocumentIngestion(file, mode));
    } catch (requestError) {
      setError(
        getApiErrorMessage(requestError, "Document recognition could not be completed."),
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClear = () => {
    reset();
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <section className="space-y-3 rounded-lg border border-line bg-surface p-4 shadow-xs">
      <div className="flex items-start gap-3">
        <Icon name="report" className="mt-0.5 h-4 w-4 shrink-0 text-ink-muted" />
        <div className="min-w-0 flex-1 space-y-1">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-xs font-bold text-ink">
              Document OCR preview · ทดลองอ่านเอกสาร
            </h2>
            <span className="font-mono text-[10px] font-bold text-ink-muted">
              NO CASE CREATED
            </span>
          </div>
          <p className="text-[11px] leading-relaxed text-ink-secondary">
            Typhoon reads the full page. Region classification and HTR are currently
            disabled, so handwriting still requires manual review.
          </p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <label htmlFor="document-ingestion-file" className="text-[11px] font-bold text-ink">
              PDF, DOCX, PNG, or JPEG
            </label>
            {fileName && !file && (
              <span className="font-mono text-[10px] text-ink-muted">
                Restored: {fileName}
              </span>
            )}
          </div>
          <input
            id="document-ingestion-file"
            ref={fileInputRef}
            aria-label="Document for OCR preview"
            type="file"
            accept={ACCEPTED_TYPES}
            disabled={isProcessing}
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
            }}
            className="block w-full rounded border border-line bg-canvas px-2.5 py-2 text-[11px] text-ink file:mr-3 file:rounded file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-[11px] file:font-bold file:text-ivory disabled:opacity-60"
          />
        </div>
        <div className="space-y-1">
          <label htmlFor="document-ingestion-mode" className="text-[11px] font-bold text-ink">
            Recognition mode
          </label>
          <select
            id="document-ingestion-mode"
            value={mode}
            disabled={isProcessing}
            onChange={(event) => setMode(event.target.value as DocumentIngestionMode)}
            className="block w-full rounded border border-line bg-canvas px-2.5 py-2 text-[11px] text-ink"
          >
            <option value="unified">Unified whole-page OCR</option>
            <option value="routed">Routed contract (classification disabled)</option>
          </select>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-[10px] text-ink-muted">
          Preview output is untrusted and is not sent to case analysis, RAG, or MITRE.
        </p>
        <div className="flex items-center gap-2">
          {(file || result || error || fileName) && (
            <button
              type="button"
              disabled={isProcessing}
              onClick={handleClear}
              className="inline-flex min-h-9 items-center rounded border border-line bg-surface px-3 py-2 text-[11px] font-semibold text-ink-secondary hover:bg-surface-hover hover:text-ink disabled:opacity-50"
            >
              Clear preview
            </button>
          )}
          <button
            type="button"
            disabled={!file || isProcessing}
            onClick={() => void processDocument()}
            className="inline-flex min-h-9 items-center rounded bg-primary px-4 py-2 text-[11px] font-bold text-ivory hover:bg-charcoal-hover disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled"
          >
            {isProcessing ? "Processing document…" : "Run OCR preview"}
          </button>
        </div>
      </div>

      {error && (
        <div role="alert" className="rounded border border-red-300 bg-red-50 p-3 text-xs text-red-900">
          {error}
        </div>
      )}
      {result && <DocumentIngestionResult result={result} />}
    </section>
  );
}
