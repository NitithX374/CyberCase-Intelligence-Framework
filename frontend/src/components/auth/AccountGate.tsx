"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

/**
 * Nothing is public except signing in.
 *
 * The root path redirects to the case library (see next.config.ts), so every
 * page a reader can reach is either the workspace or the way into it.
 */
export function AccountGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isAuthPage = pathname === "/login" || pathname === "/register";
  const { user, isLoading, sessionError, refetchSession } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    // Already signed in, and looking at the sign-in page: go back to work.
    if (isAuthPage && user) {
      const saved = localStorage.getItem(`cybercase:${user.id}:route`);
      router.replace(saved?.startsWith("/case/") ? saved : "/case");
      return;
    }

    if (!isAuthPage && !user && !sessionError) {
      router.replace(`/login?redirect=${encodeURIComponent(pathname)}`);
      return;
    }

    // Where to come back to, next time.
    if (user && !isAuthPage) {
      localStorage.setItem(`cybercase:${user.id}:route`, pathname);
    }
  }, [isAuthPage, isLoading, pathname, router, sessionError, user]);

  if (isAuthPage) return <>{children}</>;

  if (sessionError) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center bg-surface p-10 text-center text-ink">
        <p className="text-base font-semibold text-ink">Unable to check your session.</p>
        <p className="mt-1 text-sm text-ink-muted">The server could not be reached.</p>
        <button type="button" onClick={() => void refetchSession()} className="btn-primary mt-6">
          Try again
        </button>
      </main>
    );
  }

  if (isLoading || !user) {
    return (
      <main
        className="flex min-h-screen items-center justify-center bg-surface p-10"
        role="status"
        aria-label="Checking your session"
      >
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-line-strong border-t-ink" />
      </main>
    );
  }

  return <div key={user.id}>{children}</div>;
}
