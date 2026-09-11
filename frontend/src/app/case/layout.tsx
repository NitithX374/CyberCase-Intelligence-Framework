import type { ReactNode } from "react";

import { ChatWorkspace } from "@/components/ChatWorkspace";

interface CaseLayoutProps {
  children: ReactNode;
}

export default function CaseLayout({ children }: CaseLayoutProps) {
  return (
    <>
      <ChatWorkspace />
      {children}
    </>
  );
}
