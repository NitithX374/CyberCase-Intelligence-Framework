"use client";

import { Dialog } from "./Dialog";

export interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  description?: string;
  confirmLabel: string;
  confirmLoadingLabel?: string;
  cancelLabel?: string;
  isProcessing?: boolean;
  tone?: "danger" | "neutral";
  onCancel: () => void;
  onConfirm: () => void;
  titleId?: string;
  descriptionId?: string;
}

export function ConfirmDialog({
  isOpen,
  title,
  description,
  confirmLabel,
  confirmLoadingLabel,
  cancelLabel = "Cancel",
  isProcessing = false,
  tone = "neutral",
  onCancel,
  onConfirm,
  titleId = "confirm-dialog-title",
  descriptionId = "confirm-dialog-description",
}: ConfirmDialogProps) {
  return (
    <Dialog
      isOpen={isOpen}
      onDismiss={onCancel}
      canDismiss={!isProcessing}
      labelledBy={titleId}
      describedBy={description ? descriptionId : undefined}
    >
      <h2 id={titleId} className="text-base font-semibold tracking-tight">
        {title}
      </h2>
      {description && (
        <p id={descriptionId} className="mt-1.5 text-sm leading-6 text-ink-secondary">
          {description}
        </p>
      )}
      <div className="mt-6 flex flex-wrap justify-end gap-2">
        <button
          type="button"
          data-autofocus
          disabled={isProcessing}
          onClick={onCancel}
          className="btn-ghost"
        >
          {cancelLabel}
        </button>
        <button
          type="button"
          disabled={isProcessing}
          onClick={onConfirm}
          className={`btn-primary disabled:cursor-wait ${
            tone === "danger" ? "bg-critical hover:bg-critical/90 active:bg-critical" : ""
          }`}
        >
          {isProcessing ? (confirmLoadingLabel ?? confirmLabel) : confirmLabel}
        </button>
      </div>
    </Dialog>
  );
}
