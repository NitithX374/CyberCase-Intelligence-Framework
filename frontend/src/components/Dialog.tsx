"use client";

import { useEffect, useRef, type ReactNode } from "react";

export function Dialog({
  isOpen,
  onDismiss,
  canDismiss = true,
  labelledBy,
  describedBy,
  className = "w-[min(26rem,calc(100vw-2rem))]",
  children,
}: {
  isOpen: boolean;
  onDismiss: () => void;
  canDismiss?: boolean;
  labelledBy: string;
  describedBy?: string;
  className?: string;
  children: ReactNode;
}) {
  const dialogRef = useRef<HTMLDialogElement | null>(null);

  useEffect(() => {
    const element = dialogRef.current;
    if (!element) return;
    if (isOpen && !element.open) {
      if (typeof element.showModal === "function") element.showModal();
      else element.open = true;
      element.querySelector<HTMLElement>("[data-autofocus]")?.focus();
    } else if (!isOpen && element.open) {
      if (typeof element.close === "function") element.close();
      else element.open = false;
    }
  }, [isOpen]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={labelledBy}
      aria-describedby={describedBy}
      onCancel={(event) => {
        event.preventDefault();
        if (canDismiss) onDismiss();
      }}
      className={`m-auto rounded-2xl border border-line bg-surface p-6 text-ink shadow-xl shadow-black/10 backdrop:bg-ink/30 ${className}`}
    >
      {children}
    </dialog>
  );
}
