"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { HighlightedEvidenceText } from "@/components/evidence/HighlightedEvidenceText";
import type { SourceMessageRef } from "@/lib/case-overview";
import { Icon } from "@/components/common/icons";

interface SourceEvidencePopoverProps {
  sourceRef: SourceMessageRef;
  anchorElement: HTMLElement | null;
  onClose: () => void;
  onNavigateToSource?: (messageId: string) => void;
}

export function SourceEvidencePopover({
  sourceRef,
  anchorElement,
  onClose,
  onNavigateToSource,
}: SourceEvidencePopoverProps) {
  const popoverRef = useRef<HTMLDivElement>(null);
  const [coords, setCoords] = useState<{
    top: number;
    left: number;
    isMobile: boolean;
  } | null>(null);

  useEffect(() => {
    if (!anchorElement) return;

    const updatePosition = () => {
      const isMobile = window.innerWidth < 640;
      if (isMobile) {
        setCoords({ top: 0, left: 0, isMobile: true });
        return;
      }

      const anchorRect = anchorElement.getBoundingClientRect();
      const popoverWidth = 420;
      const popoverHeight = Math.min(window.innerHeight * 0.65, 480);
      const margin = 12;

      let left = anchorRect.right + margin;
      if (left + popoverWidth > window.innerWidth - 16) {
        left = anchorRect.left - popoverWidth - margin;
      }
      if (left < 16) {
        left = Math.max(16, window.innerWidth - popoverWidth - 16);
      }

      let top = anchorRect.top - 8;
      if (top + popoverHeight > window.innerHeight - 16) {
        top = window.innerHeight - popoverHeight - 16;
      }
      if (top < 16) {
        top = 16;
      }

      setCoords({ top, left, isMobile: false });
    };

    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);

    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [anchorElement]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        onClose();
      }
    };

    const handlePointerDown = (event: PointerEvent | MouseEvent) => {
      const target = event.target as Node | null;
      if (!target) return;
      if (popoverRef.current?.contains(target)) return;
      if (anchorElement?.contains(target)) return;
      onClose();
    };

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("mousedown", handlePointerDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("mousedown", handlePointerDown);
    };
  }, [anchorElement, onClose]);

  useEffect(() => {
    popoverRef.current?.focus();
    return () => anchorElement?.focus();
  }, [anchorElement]);

  if (typeof document === "undefined" || !coords) return null;

  const content = (
    <>
      {coords.isMobile && (
        <div
          className="fixed inset-0 z-40 bg-charcoal/30 backdrop-blur-[2px] transition-opacity"
          aria-hidden="true"
          onClick={onClose}
        />
      )}

      <div
        ref={popoverRef}
        role="dialog"
        aria-modal={coords.isMobile}
        aria-label={`Source Evidence: ${sourceRef.sourceTypeLabel}`}
        tabIndex={-1}
        style={
          coords.isMobile
            ? undefined
            : {
                top: `${coords.top}px`,
                left: `${coords.left}px`,
              }
        }
        className={`z-50 flex flex-col rounded-lg border border-line bg-surface text-ink shadow-xl shadow-black/10 outline-none transition-all ${
          coords.isMobile
            ? "fixed inset-x-3 bottom-4 max-h-[75vh]"
            : "fixed w-[420px] max-w-[calc(100vw-32px)] max-h-[65vh]"
        } border-l-[3px] border-l-[#356C8A]`}
      >
        <header className="flex items-start justify-between gap-3 border-b border-line px-4 py-3 bg-surface-nested/20">
          <div className="space-y-0.5 min-w-0 flex-1">
            <span className="font-mono text-[9.5px] font-bold tracking-widest text-[#356C8A] uppercase">
              SOURCE FROM CASE · พยานหลักฐานในสำนวน
            </span>
            <h3 className="text-xs font-bold text-ink truncate">
              {sourceRef.sourceTypeLabel}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close source inspector"
            className="flex h-6 w-6 shrink-0 items-center justify-center rounded text-ink-secondary hover:bg-surface-hover hover:text-ink transition-colors"
          >
            <Icon name="close" className="h-3.5 w-3.5" />
          </button>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto p-4 space-y-3">
          {sourceRef.pageNumbers.length > 0 && (
            <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-ink-muted">
              Cited document page{sourceRef.pageNumbers.length === 1 ? "" : "s"}
            </p>
          )}
          <div className="rounded border border-line/60 bg-canvas/60 p-3">
            <p className="whitespace-pre-wrap text-xs leading-relaxed text-ink font-normal select-text">
              <HighlightedEvidenceText
                content={sourceRef.displayContent || sourceRef.excerpt || "(No text content)"}
                exactQuote={sourceRef.exactQuote}
              />
            </p>
          </div>
          {sourceRef.exactQuote && (
            <p className="text-[10px] leading-relaxed text-ink-muted">
              Highlighted text is the exact passage validated against the submitted case material.
            </p>
          )}
        </div>

        {onNavigateToSource && (
          <footer className="flex items-center justify-between border-t border-line/70 px-4 py-2 bg-surface-nested/10 text-[11px]">
            <span className="text-ink-muted">
              Referenced in Case Overview
            </span>
            <button
              type="button"
              onClick={() => {
                onNavigateToSource(sourceRef.id);
                onClose();
              }}
              className="font-bold text-primary hover:underline inline-flex items-center gap-1"
            >
              <span>View in Chat</span>
              <span>↗</span>
            </button>
          </footer>
        )}
      </div>
    </>
  );

  return createPortal(content, document.body);
}
