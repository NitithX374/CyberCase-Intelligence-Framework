"use client";

import { ConfirmDialog } from "@/components/ConfirmDialog";

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
