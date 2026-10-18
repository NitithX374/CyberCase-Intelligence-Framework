"use client";

import { useCallback, useRef, useState } from "react";
import { Icon } from "@/components/icons";
import { useDismiss } from "@/lib/useDismiss";

export function AddSourceMenu({
  isUploading,
  isAnalysing,
  onOpenNarrative,
  onPickFile,
}: {
  isUploading: boolean;
  isAnalysing: boolean;
  onOpenNarrative: () => void;
  onPickFile: () => void;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const close = useCallback(() => setIsOpen(false), []);
  useDismiss(containerRef, isOpen, close);

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={isOpen}
        disabled={isUploading || isAnalysing}
        onClick={() => setIsOpen((open) => !open)}
        title={isAnalysing ? "Wait for the analysis to finish" : undefined}
        className="btn-primary h-8 px-3"
      >
        <Icon name="plus" className="h-4 w-4" />
        Add source
      </button>

      {isOpen && (
        <div
          role="menu"
          className="absolute right-0 top-9 z-20 w-52 overflow-hidden rounded-xl border border-line bg-surface p-1.5 shadow-lg shadow-black/5"
        >
          <button
            type="button"
            role="menuitem"
            disabled={isAnalysing}
            onClick={() => {
              setIsOpen(false);
              onOpenNarrative();
            }}
            className="flex h-9 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-[13px] text-ink hover:bg-surface-hover disabled:text-ink-disabled disabled:hover:bg-transparent"
          >
            Case narrative
          </button>
          <button
            type="button"
            role="menuitem"
            disabled={isAnalysing}
            onClick={() => {
              setIsOpen(false);
              onPickFile();
            }}
            className="flex h-9 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-[13px] text-ink hover:bg-surface-hover disabled:text-ink-disabled disabled:hover:bg-transparent"
          >
            File
          </button>
        </div>
      )}
    </div>
  );
}
