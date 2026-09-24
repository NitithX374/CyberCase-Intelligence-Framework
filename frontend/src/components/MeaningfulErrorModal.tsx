"use client";

import { Icon } from "./icons";
import { Dialog } from "./Dialog";
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
  if (!isOpen || !error) return null;
  const canRetry = error.retryable && Boolean(onRetry);

  return (
    <Dialog
      isOpen
      onDismiss={onClose}
      labelledBy="meaningful-error-title"
      describedBy="meaningful-error-message"
      className="w-[min(28rem,calc(100vw-2rem))]"
    >
      <div className="flex items-start justify-between gap-3">
        <h2 id="meaningful-error-title" className="text-base font-semibold tracking-tight">
          {error.title}
        </h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="ปิดหน้าต่างข้อผิดพลาด"
          className="icon-btn -mt-1 -mr-1 h-7 w-7"
        >
          <Icon name="close" className="h-4 w-4" />
        </button>
      </div>
      <p id="meaningful-error-message" className="mt-1.5 text-sm leading-6 text-ink-secondary">
        {error.message}
      </p>

      {error.technicalDetail && (
        <details className="mt-4 text-xs">
          <summary className="cursor-pointer font-medium text-ink-muted hover:text-ink">
            Technical details
          </summary>
          <p className="mt-2 font-mono break-all whitespace-pre-wrap text-ink-secondary select-text">
            {error.technicalDetail}
          </p>
        </details>
      )}

      <div className="mt-6 flex flex-wrap justify-end gap-2">
        <button
          type="button"
          data-autofocus={!canRetry || undefined}
          onClick={onClose}
          className="btn-ghost"
        >
          ปิด
        </button>
        {canRetry && (
          <button type="button" data-autofocus onClick={onRetry} className="btn-primary">
            {error.actionLabel ?? "ลองอีกครั้ง"}
          </button>
        )}
      </div>
    </Dialog>
  );
}
