"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";

export function AccountGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isLoading, sessionError, refetchSession } = useAuth();

  const isLandingPage = pathname === "/";
  const isAuthPage = pathname === "/login" || pathname === "/register";
  const isPublicPage = isLandingPage || isAuthPage;

  useEffect(() => {
    // If authenticated user visits login or register, redirect them to their workspace
    if (isAuthPage && !isLoading && user) {
      const savedRoute = localStorage.getItem(`cybercase:${user.id}:route`);
      const targetRoute =
        savedRoute && (savedRoute.startsWith("/case/") || savedRoute.startsWith("/chat/"))
          ? savedRoute
          : "/case";
      router.replace(targetRoute);
      return;
    }

    // If unauthenticated user tries to access protected routes (e.g. /chat), redirect to login
    if (!isPublicPage && !isLoading && !user && !sessionError) {
      const redirectTarget = encodeURIComponent(pathname);
      router.replace(`/login?redirect=${redirectTarget}`);
      return;
    }

    // Remember last route for authenticated user
    if (user && !isAuthPage && !isLandingPage) {
      localStorage.setItem(`cybercase:${user.id}:route`, pathname);
    }
  }, [isLoading, pathname, isPublicPage, isAuthPage, isLandingPage, router, sessionError, user]);

  // Landing page and auth pages are public: render directly
  if (isPublicPage) {
    return <>{children}</>;
  }

  // If there's a fatal session check error on protected routes
  if (sessionError) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center bg-canvas p-10 text-center text-ink">
        <div className="max-w-md rounded-2xl border border-line bg-surface p-8 shadow-sm">
          <p className="font-semibold text-critical">Unable to check your session.</p>
          <p className="mt-2 text-sm text-ink-secondary">We could not verify your login status with the server.</p>
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

  // Loading state for protected routes
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
