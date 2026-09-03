"use client";

import { useRef } from "react";
import { Icon } from "@/components/common/icons";
import { getApiErrorMessage } from "@/lib/api";
import {
  generateOcrIdempotencyKey,
  previewDocumentIngestion,
  type DocumentIngestionMode,
} from "@/lib/document-ingestion";
import { useDocumentIngestion } from "@/lib/document-ingestion-store";
import { DocumentIngestionResult } from "./DocumentIngestionResult";
import type { CaseNarrativeDraft } from "@/lib/case-narrative-document";

const ACCEPTED_TYPES = ".pdf,.docx,.png,.jpg,.jpeg";

interface DocumentIngestionPreviewProps {
  caseKey?: string;
  onUseAsNarrative?: (draft: CaseNarrativeDraft) => void;
}

export function DocumentIngestionPreview({
  caseKey = "draft",
  onUseAsNarrative,
}: DocumentIngestionPreviewProps = {}) {
  const {
    file,
    fileName,
    mode,
    isProcessing,
    result,
    error,
    idempotencyKey,
    setFile,
    setMode,
    setIsProcessing,
    setResult,
    setError,
    reset,
  } = useDocumentIngestion(caseKey);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const processDocument = async () => {
    if (!file || isProcessing) return;
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      const activeIdempotencyKey =
        idempotencyKey ?? generateOcrIdempotencyKey(caseKey, file, mode);
      setResult(
        await previewDocumentIngestion(file, mode, {
          caseKey,
          idempotencyKey: activeIdempotencyKey,
        }),
      );
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
    <section className="workspace-card space-y-4 p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-surface-nested text-ink-secondary">
          <Icon name="intake" className="h-4 w-4" />
        </span>
        <div className="min-w-0 flex-1 space-y-1">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="section-eyebrow">DOCUMENT SOURCE</p>
              <h2 className="mt-1 text-sm font-extrabold tracking-tight text-ink">
                Document OCR preview · ทดลองอ่านเอกสาร
              </h2>
            </div>
          </div>
          <p className="text-xs leading-relaxed text-ink-secondary">
            Extract text from one document. Handwritten content requires manual transcription.
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
            className="block w-full rounded-lg border border-line bg-canvas px-2.5 py-2 text-[11px] text-ink file:mr-3 file:rounded file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-[11px] file:font-bold file:text-ivory disabled:opacity-60"
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
            className="block w-full rounded-lg border border-line bg-canvas px-2.5 py-2 text-[11px] text-ink outline-none focus-visible:ring-1 focus-visible:ring-primary"
          >
            <option value="unified">Unified whole-page OCR</option>
            <option value="routed">Routed contract (classification disabled)</option>
          </select>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
        <p className="text-[10px] text-ink-muted">
          Review the extracted text before adding it to the case.
        </p>
        <div className="flex items-center gap-2">
          {(file || result || error || fileName) && (
            <button
              type="button"
              disabled={isProcessing}
              onClick={handleClear}
            className="btn-secondary inline-flex min-h-9 items-center rounded-lg"
            >
              Clear preview
            </button>
          )}
          <button
            type="button"
            disabled={!file || isProcessing}
            onClick={() => void processDocument()}
            className="btn-primary inline-flex min-h-9 items-center rounded-lg"
          >
            {isProcessing ? "Processing document…" : "Run OCR preview"}
          </button>
        </div>
      </div>

      {error && (
        <div role="alert" className="rounded-xl border border-critical/30 bg-critical/5 p-3 text-xs text-critical">
          {error}
        </div>
      )}
      {result && (
        <DocumentIngestionResult
          result={result}
          onUseAsNarrative={onUseAsNarrative}
        />
      )}
    </section>
  );
}
