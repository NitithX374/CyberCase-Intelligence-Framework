"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { SignOutDialog } from "@/components/common/SignOutDialog";

export function UserProfileMenu() {
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
      <div className="flex items-center gap-2 px-1 py-1 text-xs text-ink-muted" role="status">
        <span className="h-2 w-2 rounded-full bg-ink-muted/40 animate-pulse" />
        <span>Loading…</span>
      </div>
    );
  }

  if (!user) {
    return (
      <Link
        href="/login"
        className="flex w-full items-center justify-between rounded-lg border border-line bg-surface/50 px-2.5 py-2 text-xs font-semibold text-ink transition hover:border-line-strong hover:bg-surface hover:text-accent"
      >
        <span>Sign in</span>
        <span aria-hidden="true" className="text-[10px] text-ink-muted">→</span>
      </Link>
    );
  }

  const initial = user.name
    ? user.name.trim().charAt(0).toUpperCase()
    : user.email
      ? user.email.trim().charAt(0).toUpperCase()
      : "U";

  return (
    <div className="flex w-full flex-col gap-1.5">
      <div className="flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          <div
            aria-hidden="true"
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-ivory"
          >
            {initial}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-bold text-ink" title={user.name}>
              {user.name}
            </p>
            <p className="truncate text-[10px] text-ink-muted" title={user.email}>
              {user.email}
            </p>
          </div>
        </div>
        <button
          type="button"
          disabled={isLoggingOut}
          onClick={() => {
            setError(null);
            setIsSignOutDialogOpen(true);
          }}
          className="shrink-0 rounded-md border border-line px-2 py-1 text-[10px] font-bold text-ink-secondary outline-none transition hover:border-line-strong hover:bg-surface-hover hover:text-critical focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
        >
          {isLoggingOut ? "Signing out…" : "Sign out"}
        </button>
      </div>
      {error && (
        <span role="alert" className="text-[10px] text-critical">
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
