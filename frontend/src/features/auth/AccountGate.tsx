"use client";

import { useEffect, type ReactNode } from "react";
import { AppSkeleton } from "@/components/AppSkeleton";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "./useAuth";

export function AccountGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isAuthPage = pathname === "/login" || pathname === "/register";
  const { user, isLoading, sessionError, sessionFailures = 0, refetchSession } = useAuth();
  const waitingForServer = !user && (Boolean(sessionError) || (isLoading && sessionFailures > 0));

  useEffect(() => {
    if (isLoading) return;

    if (isAuthPage && user) {
      const saved = localStorage.getItem(`cybercase:${user.id}:route`);
      router.replace(saved?.startsWith("/case/") ? saved : "/case");
      return;
    }

    if (!isAuthPage && !user && !sessionError) {
      router.replace("/login");
      return;
    }

    if (user && !isAuthPage) {
      localStorage.setItem(`cybercase:${user.id}:route`, pathname);
    }
  }, [isAuthPage, isLoading, pathname, router, sessionError, user]);

  if (isAuthPage) return <>{children}</>;

  if (waitingForServer) {
    return <ServerUnreachable attempts={sessionFailures} onRetry={refetchSession} />;
  }

  if (isLoading || !user) {
    return (
      <AppSkeleton
        title="Opening CyberCase…"
        detail="Checking your session. Your cases appear in a moment."
      />
    );
  }

  return <div key={user.id}>{children}</div>;
}

const RETRY_EVERY_MS = 5_000;

function ServerUnreachable({ attempts, onRetry }: { attempts: number; onRetry: () => unknown }) {
  useEffect(() => {
    const timer = window.setInterval(() => {
      void onRetry();
    }, RETRY_EVERY_MS);
    return () => window.clearInterval(timer);
  }, [onRetry]);

  return (
    <AppSkeleton
      title="Unable to check your session."
      detail="The server is not answering yet. Right after the computer starts it is still loading its reading models, which takes about a minute. This page keeps trying on its own."
    >
      <div className="mt-5 flex flex-wrap items-center gap-4">
        <button type="button" onClick={() => void onRetry()} className="btn-on-band">
          Try again now
        </button>
        <span className="text-sm text-white">
          {attempts <= 1
            ? "Trying again in a few seconds"
            : `Tried ${attempts} times, still waiting`}
        </span>
      </div>
    </AppSkeleton>
  );
}
