"use client";

import { useCallback, useRef, useState } from "react";
import { useAuth } from "./useAuth";
import { useDismiss } from "@/lib/useDismiss";
import { UserProfileMenu, type AccountMenuAction } from "./UserProfileMenu";

/** The avatar in the corner, and the few things that live behind it. */
export function AccountMenu({ actions = [] }: { actions?: AccountMenuAction[] }) {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const close = useCallback(() => setIsOpen(false), []);
  useDismiss(containerRef, isOpen, close);

  const initial = (user?.name || user?.email || "?").trim().charAt(0).toUpperCase();

  return (
    <div ref={containerRef} className="relative shrink-0">
      <button
        type="button"
        aria-label="Open account menu"
        aria-haspopup="menu"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((open) => !open)}
        className="flex h-8 w-8 items-center justify-center rounded-full bg-surface-nested text-[13px] font-semibold text-ink-secondary transition-colors hover:bg-line hover:text-ink"
      >
        {initial}
      </button>
      {isOpen && (
        <div className="absolute right-0 top-10 z-50 w-64 rounded-xl border border-line bg-surface p-1.5 shadow-lg shadow-black/5">
          <UserProfileMenu actions={actions} onAction={close} />
        </div>
      )}
    </div>
  );
}
