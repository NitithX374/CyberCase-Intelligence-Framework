"use client";

import { Icon } from "@/components/icons";
import { useBlobUrl } from "@/lib/useBlobUrl";
import { fetchCaseDocumentContent } from "./api";
import type { FileItem } from "./FileSourcePreview";
import { ViewportMessage } from "./ViewportMessage";

export function OriginalFilePreview({ caseId, item }: { caseId: string; item: FileItem }) {
  const { documentId } = item;
  const filename = item.source.filename ?? "";
  const mimeType = item.source.mime_type ?? "";
  const { blob, attach, isLoading, error, refetch } = useBlobUrl(
    ["case-document-content", caseId, documentId],
    (signal) => fetchCaseDocumentContent(caseId, documentId, signal),
  );

  if (isLoading) {
    return (
      <div
        role="status"
        aria-label="Loading original file"
        className="flex h-full min-h-[24rem] items-center justify-center text-ink-muted"
      >
        <Icon name="spinner" className="h-6 w-6" />
      </div>
    );
  }
  if (error || !blob) {
    return (
      <ViewportMessage title="The original file could not be loaded.">
        <button
          type="button"
          onClick={() => void refetch()}
          className="btn-secondary mt-4 h-8 px-3"
        >
          Try again
        </button>
      </ViewportMessage>
    );
  }

  const canEmbed = mimeType === "application/pdf" || mimeType.startsWith("image/");
  if (!canEmbed) {
    return (
      <ViewportMessage title="This file type has no preview.">
        <a ref={attach} download={filename} className="btn-primary mt-4">
          <Icon name="download" className="h-4 w-4" />
          Download file
        </a>
      </ViewportMessage>
    );
  }

  return (
    <iframe
      ref={attach}
      title={`Original file: ${filename}`}
      className="h-full min-h-[28rem] w-full border-0 bg-surface"
    />
  );
}
