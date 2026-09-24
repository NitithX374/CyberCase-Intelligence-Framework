"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";

interface WorkspaceActivityValue {
  isFollowupPending: boolean;
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
