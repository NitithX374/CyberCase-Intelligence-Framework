"use client";

import { useRef } from "react";
import { Icon } from "@/components/common/icons";
import { getApiErrorMessage } from "@/lib/api";
import {
  generateOcrIdempotencyKey,
  previewDocumentIngestion,
} from "@/lib/document-ingestion";
import { useDocumentIngestion } from "@/lib/document-ingestion-store";
import { DocumentIngestionResult } from "./DocumentIngestionResult";
import type { CaseNarrativeDraft } from "@/lib/case-narrative-document";

const ACCEPTED_TYPES = ".pdf,.docx,.png,.jpg,.jpeg";

interface DocumentIngestionPreviewProps {
  caseKey?: string;
  disabled?: boolean;
  showResult?: boolean;
  onUseAsNarrative?: (draft: CaseNarrativeDraft) => void;
}

export function DocumentIngestionPreview({
  caseKey = "draft",
  disabled = false,
  showResult = true,
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
    setIsProcessing,
    setResult,
    setError,
    reset,
  } = useDocumentIngestion(caseKey);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const processDocument = async () => {
    if (!file || isProcessing || disabled) return;
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
    <div aria-label="Document attachment" className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <input
          id="document-ingestion-file"
          ref={fileInputRef}
          aria-label="Document for OCR preview"
          type="file"
          accept={ACCEPTED_TYPES}
          disabled={isProcessing || disabled}
          onChange={(event) => {
            const selectedFile = event.target.files?.[0];
            if (selectedFile) setFile(selectedFile);
          }}
          className="hidden"
        />
        <button
          type="button"
          disabled={isProcessing || disabled}
          onClick={() => fileInputRef.current?.click()}
          className="inline-flex min-h-9 items-center gap-2 rounded-md px-2 text-xs font-medium text-ink outline-none hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
        >
          <Icon name="intake" className="h-4 w-4" />
          {fileName ? "Replace material" : "Add material"}
        </button>
        <div className="flex flex-wrap items-center gap-2">
          {(file || result || error || fileName) && (
            <button
              type="button"
              disabled={isProcessing || disabled}
              onClick={handleClear}
              className="min-h-9 rounded-md px-2 text-xs text-ink-secondary hover:text-ink focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
            >
              Clear preview
            </button>
          )}
          <button
            type="button"
            disabled={!file || isProcessing || disabled}
            onClick={() => void processDocument()}
            className="btn-secondary inline-flex min-h-9 items-center rounded-md disabled:cursor-not-allowed disabled:border-line disabled:text-ink-disabled"
          >
            {isProcessing ? "Extracting text…" : error ? "Retry extraction" : "Extract text"}
          </button>
        </div>
      </div>

      <p className="text-[11px] text-ink-muted">PDF, DOCX, PNG, JPEG · One document at a time</p>

      {error && (
        <div role="alert" className="border-l-2 border-critical pl-3 text-xs text-ink">
          <p>Text extraction failed. Retry or choose another document.</p>
          <details className="mt-2 text-ink-muted"><summary className="cursor-pointer">Error details</summary><p className="mt-2 break-words">{error}</p></details>
        </div>
      )}
      {showResult && result && (
        <div className="pt-4">
          <DocumentIngestionResult
            result={result}
            onUseAsNarrative={disabled ? undefined : onUseAsNarrative}
          />
        </div>
      )}
    </div>
  );
}
