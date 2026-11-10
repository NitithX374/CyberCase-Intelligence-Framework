"use client";

import { useState } from "react";
import Link from "next/link";
import * as Menu from "@radix-ui/react-dropdown-menu";
import { useAuth } from "./useAuth";
import { Icon, type IconName } from "@/components/icons";
import { ConfirmDialog } from "@/components/ConfirmDialog";

interface AccountMenuAction {
  label: string;
  icon: IconName;
  href?: string;
  onSelect?: () => void;
  disabled?: boolean;
}

const itemClass =
  "flex h-9 w-full cursor-pointer items-center gap-2.5 rounded-lg px-2.5 text-left text-sm text-ink outline-none transition-colors data-[highlighted]:bg-surface-hover data-[disabled]:cursor-wait data-[disabled]:opacity-50";

export function AccountMenu({ actions = [] }: { actions?: AccountMenuAction[] }) {
  const { user, isLoading, logout, isLoggingOut } = useAuth();
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const initial = (user?.name || user?.email || "?").trim().charAt(0).toUpperCase();

  const signOut = async () => {
    setError(null);
    try {
      await logout();
    } catch {
      setError("Sign out failed. Try again.");
    }
    setConfirming(false);
  };

  return (
    <span className="relative shrink-0">
      <Menu.Root modal={false}>
        <Menu.Trigger asChild>
          <button
            type="button"
            aria-label="Open account menu"
            className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-soft text-sm font-bold text-primary transition-colors hover:bg-primary-line data-[state=open]:bg-primary-line"
          >
            {initial}
          </button>
        </Menu.Trigger>
        <Menu.Portal>
          <Menu.Content
            align="end"
            sideOffset={6}
            className="pop-in z-50 w-64 rounded-xl border border-line bg-surface p-1.5 shadow-lg shadow-black/5 [--origin:top_right]"
          >
            {isLoading ? (
              <p role="status" className="px-2.5 py-2 text-sm text-ink-muted">
                Loading…
              </p>
            ) : !user ? (
              <Menu.Item asChild className={itemClass}>
                <Link href="/login">
                  <Icon name="account" className="h-4 w-4 text-ink-muted" />
                  Sign in
                </Link>
              </Menu.Item>
            ) : (
              <>
                <Menu.Label className="min-w-0 px-2.5 pt-1.5 pb-2.5">
                  <span className="block truncate text-sm font-semibold text-ink" title={user.name}>
                    {user.name}
                  </span>
                  <span className="block truncate text-xs text-ink-muted" title={user.email}>
                    {user.email}
                  </span>
                </Menu.Label>
                {actions.length > 0 && (
                  <>
                    <Menu.Separator className="my-1 h-px bg-line" />
                    {actions.map((action) =>
                      action.href ? (
                        <Menu.Item key={action.label} asChild className={itemClass}>
                          <Link href={action.href}>
                            <Icon name={action.icon} className="h-4 w-4 text-ink-muted" />
                            {action.label}
                          </Link>
                        </Menu.Item>
                      ) : (
                        <Menu.Item
                          key={action.label}
                          disabled={action.disabled}
                          onSelect={action.onSelect}
                          className={itemClass}
                        >
                          <Icon name={action.icon} className="h-4 w-4 text-ink-muted" />
                          {action.label}
                        </Menu.Item>
                      ),
                    )}
                  </>
                )}
                <Menu.Separator className="my-1 h-px bg-line" />
                <Menu.Item
                  disabled={isLoggingOut}
                  onSelect={() => {
                    setError(null);
                    setConfirming(true);
                  }}
                  className={itemClass}
                >
                  <Icon name="log-out" className="h-4 w-4 text-ink-muted" />
                  {isLoggingOut ? "Signing out…" : "Sign out"}
                </Menu.Item>
              </>
            )}
          </Menu.Content>
        </Menu.Portal>
      </Menu.Root>
      {error && (
        <span
          role="alert"
          className="absolute top-12 right-0 z-50 w-max rounded-lg border border-line bg-surface px-3 py-2 text-xs text-critical shadow-lg shadow-black/5"
        >
          {error}
        </span>
      )}
      <ConfirmDialog
        isOpen={confirming}
        title="Sign out of CyberCase?"
        confirmLabel="Sign out"
        confirmLoadingLabel="Signing out…"
        isProcessing={isLoggingOut}
        onCancel={() => setConfirming(false)}
        onConfirm={() => void signOut()}
        titleId="signout-dialog-title"
      />
    </span>
  );
}
