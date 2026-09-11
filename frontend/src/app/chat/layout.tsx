"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";

interface ChatLayoutProps {
  children: ReactNode;
}

export default function ChatLayout({ children }: ChatLayoutProps) {
  const router = useRouter();

  useEffect(() => {
    router.replace("/case");
  }, [router]);

  return <>{children}</>;
}
