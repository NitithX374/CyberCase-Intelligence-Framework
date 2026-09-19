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
      <main className="flex min-h-screen flex-col items-center justify-center bg-canvas p-10 text-center text-ink">
        <div className="max-w-md rounded-2xl border border-line bg-surface p-8 shadow-sm">
          <p className="font-semibold text-critical">Unable to check your session.</p>
          <p className="mt-2 text-sm text-ink-secondary">
            We could not verify your login status with the server.
          </p>
          <button
            onClick={() => void refetchSession()}
            className="mt-6 rounded-lg bg-primary px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-ivory transition hover:bg-charcoal-hover"
          >
            Try again
          </button>
        </div>
      </main>
    );
  }

  if (isLoading || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-canvas p-10" role="status">
        <div className="flex items-center gap-3 text-xs font-mono tracking-widest text-ink-secondary">
          <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          VERIFYING WORKSPACE ACCESS…
        </div>
      </main>
    );
  }

  return <div key={user.id}>{children}</div>;
}
