"use client";

import { useEffect, useRef } from "react";
import { Icon } from "./icons";
import type { UserFacingError } from "@/lib/userFacingError";

export interface MeaningfulErrorModalProps {
  isOpen: boolean;
  error: UserFacingError | null;
  onClose: () => void;
  onRetry?: () => void;
}

export function MeaningfulErrorModal({
  isOpen,
  error,
  onClose,
  onRetry,
}: MeaningfulErrorModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedElementRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen || !error) return;

    previouslyFocusedElementRef.current = document.activeElement as HTMLElement | null;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key === "Tab") {
        if (!modalRef.current) return;
        const focusableElements = modalRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), details',
        );
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    const timer = window.setTimeout(() => {
      if (!modalRef.current) return;
      const primaryBtn = modalRef.current.querySelector<HTMLElement>('[data-autofocus="true"]');
      if (primaryBtn) {
        primaryBtn.focus();
      } else {
        const firstFocusable = modalRef.current.querySelector<HTMLElement>("button");
        firstFocusable?.focus();
      }
    }, 50);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      window.clearTimeout(timer);
      if (previouslyFocusedElementRef.current) {
        previouslyFocusedElementRef.current.focus();
      }
    };
  }, [isOpen, error, onClose]);

  if (!isOpen || !error) return null;

  const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      role="presentation"
      onClick={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4 backdrop-blur-[2px]"
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="meaningful-error-title"
        aria-describedby="meaningful-error-message"
        className="relative w-full max-w-md rounded-2xl border border-line bg-surface p-6 shadow-2xl shadow-black/10"
      >
        <div className="flex items-start gap-3.5">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-critical/[0.08] text-critical">
            <Icon name="error" className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1 pt-0.5">
            <h2
              id="meaningful-error-title"
              className="text-base font-semibold tracking-tight text-ink"
            >
              {error.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="ปิดหน้าต่างข้อผิดพลาด"
            className="shrink-0 -mr-1 -mt-1 rounded-md p-1.5 text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink focus-visible:outline-2 focus-visible:outline-primary"
          >
            <Icon name="close" className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-3.5 pl-12.5">
          <p id="meaningful-error-message" className="text-sm leading-6 text-ink-secondary">
            {error.message}
          </p>

          {error.technicalDetail && (
            <div className="mt-4">
              <details className="group rounded-lg bg-surface-nested px-3 py-2 text-xs">
                <summary className="cursor-pointer font-medium text-ink-muted transition-colors hover:text-ink select-none flex items-center justify-between">
                  <span>Technical details</span>
                  <span className="text-[10px] transition-transform duration-200 group-open:rotate-180">
                    ▾
                  </span>
                </summary>
                <div className="mt-2 border-t border-line pt-2 font-mono text-xs text-ink-secondary break-all select-text whitespace-pre-wrap">
                  {error.technicalDetail}
                </div>
              </details>
            </div>
          )}

          <div className="mt-6 flex flex-wrap items-center justify-end gap-2">
            <button type="button" onClick={onClose} className="btn-ghost">
              ปิด
            </button>
            {error.retryable && onRetry && (
              <button type="button" data-autofocus="true" onClick={onRetry} className="btn-primary">
                {error.actionLabel ?? "ลองอีกครั้ง"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
