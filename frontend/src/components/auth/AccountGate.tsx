"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";

export function AccountGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isLoading, sessionError, refetchSession } = useAuth();
  const publicPage = ["/login", "/register"].includes(pathname);
  useEffect(() => {
    if (!publicPage && !isLoading && !user && !sessionError) router.replace("/login");
    if (user && !publicPage) localStorage.setItem(`cybercase:${user.id}:route`, pathname);
  }, [isLoading, pathname, publicPage, router, sessionError, user]);
  if (publicPage) return children;
  if (sessionError) return <main className="p-10">Unable to check your session. <button onClick={() => void refetchSession()}>Try again</button></main>;
  if (isLoading || !user) return <main className="p-10" role="status">Checking your account…</main>;
  return <div key={user.id}>{children}</div>;
}
