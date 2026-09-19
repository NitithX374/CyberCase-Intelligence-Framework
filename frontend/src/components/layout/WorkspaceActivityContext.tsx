"use client";

import { createContext, useContext, type ReactNode } from "react";

interface WorkspaceActivityValue {
  isFollowupPending: boolean;
}

const defaultActivity: WorkspaceActivityValue = { isFollowupPending: false };
const WorkspaceActivityContext = createContext<WorkspaceActivityValue>(defaultActivity);

export function WorkspaceActivityProvider({
  isFollowupPending,
  children,
}: WorkspaceActivityValue & { children: ReactNode }) {
  return (
    <WorkspaceActivityContext.Provider value={{ isFollowupPending }}>
      {children}
    </WorkspaceActivityContext.Provider>
  );
}

export function useWorkspaceActivity() {
  return useContext(WorkspaceActivityContext);
}
