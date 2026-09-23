"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";

interface WorkspaceActivityValue {
  isFollowupPending: boolean;
  /**
   * Starts the case analysis. The layout owns it, because it owns what follows:
   * a question opens the chat, a finished analysis opens Analysis, and a
   * failure is shown in the workspace error modal. A page that offers the
   * button calls this rather than starting the run itself.
   */
  runAnalysis: () => void;
}

const defaultActivity: WorkspaceActivityValue = {
  isFollowupPending: false,
  runAnalysis: () => {},
};
const WorkspaceActivityContext = createContext<WorkspaceActivityValue>(defaultActivity);

export function WorkspaceActivityProvider({
  isFollowupPending,
  runAnalysis,
  children,
}: WorkspaceActivityValue & { children: ReactNode }) {
  const value = useMemo(
    () => ({ isFollowupPending, runAnalysis }),
    [isFollowupPending, runAnalysis],
  );
  return (
    <WorkspaceActivityContext.Provider value={value}>{children}</WorkspaceActivityContext.Provider>
  );
}

export function useWorkspaceActivity() {
  return useContext(WorkspaceActivityContext);
}
