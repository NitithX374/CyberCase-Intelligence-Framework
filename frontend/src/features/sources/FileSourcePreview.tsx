"use client";

import type { RailItem } from "./railItems";
import type { PreviewMode } from "./SourceViewport";
import { OriginalFilePreview } from "./OriginalFilePreview";
import { ExtractedTextPreview } from "./ExtractedTextPreview";

export type FileItem = Extract<RailItem, { kind: "file" }>;

export function FileSourcePreview({
  caseId,
  item,
  mode,
  onRetry,
  isRetrying,
}: {
  caseId: string;
  item: FileItem;
  mode: PreviewMode;
  onRetry?: () => void;
  isRetrying: boolean;
}) {
  const original = <OriginalFilePreview caseId={caseId} item={item} />;
  const extracted = (
    <ExtractedTextPreview source={item.source} onRetry={onRetry} isRetrying={isRetrying} />
  );
  if (mode === "original") return original;
  if (mode === "ocr") return extracted;
  return (
    <div className="flex h-full min-h-0 flex-col divide-y divide-line lg:flex-row lg:divide-x lg:divide-y-0">
      <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">{original}</div>
      <div className="h-1/2 min-h-0 min-w-0 flex-1 overflow-hidden lg:h-full">{extracted}</div>
    </div>
  );
}
