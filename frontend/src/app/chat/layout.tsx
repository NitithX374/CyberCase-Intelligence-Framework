"use client";

import { useEffect, useState, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { LegacyChatRouteStateView } from "@/features/chat/routing/LegacyChatRouteStateView";
import { resolveLegacyChatDestination, resolveLegacyChatRouteState } from "@/features/chat/routing/workspaceRoutes";
import { getChatCaseLink } from "@/lib/api";

interface ChatLayoutProps {
  children: ReactNode;
}

type LegacyChatResolution = "resolving" | "historical_unavailable" | "unavailable";

export default function ChatLayout({ children }: ChatLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const route = resolveLegacyChatRouteState(pathname);
  const [resolution, setResolution] = useState<{
    pathname: string;
    state: LegacyChatResolution;
  }>({ pathname: "", state: "resolving" });

  useEffect(() => {
    if (!route.threadId) {
      router.replace("/case");
      return;
    }
    const controller = new AbortController();
    let active = true;
    getChatCaseLink(route.threadId, controller.signal)
      .then((link) => {
        if (!active) return;
        const destination = resolveLegacyChatDestination(pathname, {
          status: link.status,
          case_id: link.case_id ?? null,
        });
        if (destination.kind === "case") router.replace(destination.path);
        else setResolution({ pathname, state: destination.status });
      })
      .catch(() => {
        if (active && !controller.signal.aborted) {
          const destination = resolveLegacyChatDestination(pathname, null);
          if (destination.kind === "unavailable") {
            setResolution({ pathname, state: destination.status });
          }
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [pathname, route.threadId, route.view, router]);

  if (!route.threadId) return children;
  const state = resolution.pathname === pathname ? resolution.state : "resolving";
  if (state === "historical_unavailable" || state === "unavailable") {
    return <LegacyChatRouteStateView state={state} />;
  }
  return <LegacyChatRouteStateView state="resolving" />;
}
