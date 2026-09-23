"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Icon, type IconName } from "@/components/common/icons";
import { SignOutDialog } from "@/components/common/DeleteDialog";

export interface AccountMenuAction {
  label: string;
  icon: IconName;
  href?: string;
  onSelect?: () => void;
  disabled?: boolean;
}

const itemClass =
  "flex h-9 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-[13px] text-ink transition-colors hover:bg-surface-hover disabled:cursor-wait disabled:opacity-50";

export function UserProfileMenu({
  actions = [],
  onAction,
}: {
  actions?: AccountMenuAction[];
  onAction?: () => void;
}) {
  const { user, isLoading, logout, isLoggingOut } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isSignOutDialogOpen, setIsSignOutDialogOpen] = useState(false);

  const handleSignOut = async () => {
    setError(null);
    try {
      await logout();
      setIsSignOutDialogOpen(false);
    } catch {
      setError("Sign out failed. Try again.");
      setIsSignOutDialogOpen(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-2.5 py-2 text-[13px] text-ink-muted" role="status">
        <span className="h-2 w-2 animate-pulse rounded-full bg-ink-muted/40" />
        <span>Loading…</span>
      </div>
    );
  }

  if (!user) {
    return (
      <Link href="/login" className={itemClass}>
        <Icon name="account" className="h-4 w-4 text-ink-muted" />
        <span>Sign in</span>
      </Link>
    );
  }

  return (
    <div className="flex w-full flex-col">
      <div className="min-w-0 px-2.5 pt-1.5 pb-2.5">
        <p className="truncate text-[13px] font-semibold text-ink" title={user.name}>
          {user.name}
        </p>
        <p className="truncate text-xs text-ink-muted" title={user.email}>
          {user.email}
        </p>
      </div>

      {actions.length > 0 && (
        <div className="border-t border-line py-1">
          {actions.map((action) =>
            action.href ? (
              <Link key={action.label} href={action.href} onClick={onAction} className={itemClass}>
                <Icon name={action.icon} className="h-4 w-4 text-ink-muted" />
                {action.label}
              </Link>
            ) : (
              <button
                key={action.label}
                type="button"
                disabled={action.disabled}
                onClick={() => {
                  onAction?.();
                  action.onSelect?.();
                }}
                className={itemClass}
              >
                <Icon name={action.icon} className="h-4 w-4 text-ink-muted" />
                {action.label}
              </button>
            ),
          )}
        </div>
      )}

      <div className="border-t border-line pt-1">
        <button
          type="button"
          disabled={isLoggingOut}
          onClick={() => {
            setError(null);
            setIsSignOutDialogOpen(true);
          }}
          className={itemClass}
        >
          <Icon name="log-out" className="h-4 w-4 text-ink-muted" />
          {isLoggingOut ? "Signing out…" : "Sign out"}
        </button>
      </div>
      {error && (
        <span role="alert" className="px-2.5 pb-1.5 text-xs text-critical">
          {error}
        </span>
      )}
      <SignOutDialog
        isOpen={isSignOutDialogOpen}
        isSigningOut={isLoggingOut}
        onCancel={() => setIsSignOutDialogOpen(false)}
        onConfirm={() => void handleSignOut()}
      />
    </div>
  );
}
