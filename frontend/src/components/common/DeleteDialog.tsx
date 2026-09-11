"use client";

import { useEffect, useRef } from "react";
import type { CaseRead } from "@/lib/api";

export interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  confirmLoadingLabel?: string;
  isProcessing?: boolean;
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
  isProcessing = false,
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
      aria-describedby={descriptionId}
      onCancel={(event) => {
        event.preventDefault();
        if (!isProcessing) onCancel();
      }}
      className="m-auto max-w-md rounded-lg border border-line bg-surface p-6 text-ink shadow-xl shadow-black/10 backdrop:bg-primary/35 backdrop:backdrop-blur-[1px]"
    >
      <h2 id={titleId} className="text-base font-bold tracking-tight">
        {title}
      </h2>
      <p
        id={descriptionId}
        className="mt-2 text-xs leading-relaxed text-ink-secondary"
      >
        {description}
      </p>
      <div className="mt-5 flex flex-wrap justify-end gap-2.5">
        <button
          ref={cancelButtonRef}
          type="button"
          disabled={isProcessing}
          onClick={onCancel}
          className="inline-flex min-h-8.5 items-center justify-center rounded-lg border border-line bg-surface px-3.5 text-xs font-bold text-ink outline-none transition-colors hover:border-ink hover:bg-surface-hover active:bg-control-disabled focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled"
        >
          Cancel
        </button>
        <button
          type="button"
          disabled={isProcessing}
          onClick={onConfirm}
          className="inline-flex min-h-8.5 items-center justify-center rounded-lg bg-accent px-3.5 text-xs font-bold text-ivory outline-none transition-colors hover:bg-accent-strong focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-wait disabled:bg-stone disabled:text-ink-disabled"
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
      description={`This will permanently remove ${caseRecord?.title ?? "this case"}, its message history, retrieval contexts, and reports. This action cannot be undone.`}
      confirmLabel="Delete case"
      confirmLoadingLabel="Deleting..."
      isProcessing={isDeleting}
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
      description="Are you sure you want to sign out? You will need to sign in again to access your cases, saved drafts, and analytical context."
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
