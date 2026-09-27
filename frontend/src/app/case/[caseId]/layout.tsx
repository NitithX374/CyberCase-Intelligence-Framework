import type { ReactNode } from "react";
import { CaseWorkspace } from "@/features/workspace/CaseWorkspace";

export default function CaseShellLayout({ children }: { children: ReactNode }) {
  return <CaseWorkspace>{children}</CaseWorkspace>;
}
