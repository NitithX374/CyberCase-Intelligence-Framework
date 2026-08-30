"use client";

import { useEffect, useRef } from "react";
import type { ChatThreadRead } from "@/lib/api";

interface DeleteChatDialogProps {
  thread: ChatThreadRead | null;
  isDeleting: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export function DeleteChatDialog({
  thread,
  isDeleting,
  onCancel,
  onConfirm,
}: DeleteChatDialogProps) {
  const dialogRef = useRef<HTMLDialogElement | null>(null);
  const cancelButtonRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    const element = dialogRef.current;
    if (!element) return;

    if (thread && !element.open) {
      element.showModal();
      cancelButtonRef.current?.focus();
    } else if (!thread && element.open) {
      element.close();
    }
  }, [thread]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="delete-chat-title"
      aria-describedby="delete-chat-description"
      onCancel={(event) => {
        event.preventDefault();
        if (!isDeleting) onCancel();
      }}
      className="m-auto max-w-md rounded-lg border border-line bg-surface p-6 text-ink shadow-xl shadow-black/10 backdrop:bg-primary/35 backdrop:backdrop-blur-[1px]"
    >
      <h2 id="delete-chat-title" className="text-base font-bold tracking-tight">
        Delete this case?
      </h2>
      <p
        id="delete-chat-description"
        className="mt-2 text-xs leading-relaxed text-ink-secondary"
      >
        This will permanently remove{" "}
        <span className="font-bold text-ink">
          {thread?.title ?? "this case"}
        </span>
        , its message history, retrieval contexts, and reports. This action cannot be
        undone.
      </p>
      <div className="mt-5 flex flex-wrap justify-end gap-2.5">
        <button
          ref={cancelButtonRef}
          type="button"
          disabled={isDeleting}
          onClick={onCancel}
          className="inline-flex min-h-8.5 items-center justify-center rounded-lg border border-line bg-surface px-3.5 text-xs font-bold text-ink outline-none transition-colors hover:border-ink hover:bg-surface-hover active:bg-control-disabled focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled"
        >
          Cancel
        </button>
        <button
          type="button"
          disabled={isDeleting}
          onClick={onConfirm}
          className="inline-flex min-h-8.5 items-center justify-center rounded-lg bg-accent px-3.5 text-xs font-bold text-ivory outline-none transition-colors hover:bg-accent-strong focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-wait disabled:bg-stone disabled:text-ink-disabled"
        >
          {isDeleting ? "Deleting..." : "Delete case"}
        </button>
      </div>
    </dialog>
  );
}
