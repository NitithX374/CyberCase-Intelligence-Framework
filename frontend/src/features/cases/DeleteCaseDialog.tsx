"use client";

import type { CaseRead } from "@/lib/api";
import { ConfirmDialog } from "@/components/ConfirmDialog";

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
