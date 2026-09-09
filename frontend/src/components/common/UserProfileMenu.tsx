"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";

export function UserProfileMenu() {
  const { user, isLoading, logout, isLoggingOut } = useAuth();
  const [error, setError] = useState<string | null>(null);
  if (isLoading) return <span>Loading…</span>;
  if (!user) return <Link href="/login">Sign in</Link>;
  return <div className="flex items-center gap-3 text-xs">
    <span title={user.email}>{user.name}</span>
    <button disabled={isLoggingOut} onClick={() => void logout().catch(() => setError("Sign out failed. Try again."))} className="rounded-lg border border-line px-3 py-2">{isLoggingOut ? "Signing out…" : "Sign out"}</button>
    {error && <span role="alert">{error}</span>}
  </div>;
}
