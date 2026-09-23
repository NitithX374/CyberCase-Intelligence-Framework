"use client";

import { useEffect, useRef } from "react";
import type { CaseRead } from "@/lib/api";

export interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  description?: string;
  confirmLabel: string;
  confirmLoadingLabel?: string;
  cancelLabel?: string;
  isProcessing?: boolean;
  /** A destructive action gets a red confirm button. */
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
  const dialogRef = useRef<HTMLDialogElement | null>(null);
  const cancelButtonRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    const element = dialogRef.current;
    if (!element) return;

    if (isOpen && !element.open) {
      if (typeof element.showModal === "function") {
        element.showModal();
      } else {
        element.open = true;
      }
      cancelButtonRef.current?.focus();
    } else if (!isOpen && element.open) {
      if (typeof element.close === "function") {
        element.close();
      } else {
        element.open = false;
      }
    }
  }, [isOpen]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={titleId}
      aria-describedby={description ? descriptionId : undefined}
      onCancel={(event) => {
        event.preventDefault();
        if (!isProcessing) onCancel();
      }}
      className="m-auto w-[min(26rem,calc(100vw-2rem))] rounded-2xl border border-line bg-surface p-6 text-ink shadow-2xl shadow-black/10 backdrop:bg-ink/30"
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
          ref={cancelButtonRef}
          type="button"
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
    </dialog>
  );
}

export interface DeleteCaseDialogProps {
  caseRecord: CaseRead | null;
  isDeleting: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export function DeleteCaseDialog({
  caseRecord,
  isDeleting,
  onCancel,
  onConfirm,
}: DeleteCaseDialogProps) {
  return (
    <ConfirmDialog
      isOpen={Boolean(caseRecord)}
      title="Delete this case?"
      description={`“${caseRecord?.title ?? "This case"}” and its sources, chat and reports will be permanently deleted.`}
      confirmLabel="Delete case"
      confirmLoadingLabel="Deleting…"
      isProcessing={isDeleting}
      tone="danger"
      onCancel={onCancel}
      onConfirm={onConfirm}
      titleId="delete-chat-title"
      descriptionId="delete-chat-description"
    />
  );
}

export interface SignOutDialogProps {
  isOpen: boolean;
  isSigningOut?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export function SignOutDialog({
  isOpen,
  isSigningOut = false,
  onCancel,
  onConfirm,
}: SignOutDialogProps) {
  return (
    <ConfirmDialog
      isOpen={isOpen}
      title="Sign out of CyberCase?"
      confirmLabel="Sign out"
      confirmLoadingLabel="Signing out…"
      isProcessing={isSigningOut}
      onCancel={onCancel}
      onConfirm={onConfirm}
      titleId="signout-dialog-title"
      descriptionId="signout-dialog-description"
    />
  );
}
