import type { ReactNode } from "react";

interface CaseLayoutProps {
  children: ReactNode;
}

export default function CaseLayout({ children }: CaseLayoutProps) {
  return <>{children}</>;
}
