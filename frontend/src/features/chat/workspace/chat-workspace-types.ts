import type { FormEvent } from "react";

import type {
  RunPhase,
  WorkspaceRouteView,
  WorkspaceView,
} from "@/components/common/types";
import type {
  ChatMessageAction,
  CaseIntakeSubmission,
  CaseNarrativeDocumentSource,
  ChatThreadRead,
  PersistedChatMessage,
  ThreadStatus,
} from "@/lib/api";

export interface PendingChatSubmission {
  threadId: string;
  content: string;
  key: string;
  kind: "message" | "followup";
  action?: ChatMessageAction;
  documentSources?: CaseNarrativeDocumentSource[];
  lastKnownMessageOrdinal: number;
  requestOrdinal?: number;
}

export interface ChatWorkspaceLayoutProps {
  activeThread: ChatThreadRead | null;
  activeThreadId: string | null;
  activeView: WorkspaceRouteView;
  activeWorkspaceView: WorkspaceRouteView;
  threads: ChatThreadRead[];
  threadsLoading: boolean;
  threadsError: string | null;
  creatingThread: boolean;
  deletingThreadId: string | null;
  phase: RunPhase;
  threadStatus: ThreadStatus | null;
  queryError: string | null;
  input: string;
  postAnswerAction: ChatMessageAction | null;
  visibleMessages: PersistedChatMessage[];
  hasCompletedAnalysis: boolean;
  messages: PersistedChatMessage[];
  deleteCandidate: ChatThreadRead | null;
  onSelectThread: (threadId: string) => void;
  onNewChat: () => void;
  onRequestDelete: (thread: ChatThreadRead) => void;
  onViewChange: (view: WorkspaceView) => void;
  onInputChange: (value: string) => void;
  onPostAnswerActionChange: (action: ChatMessageAction) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onSetDeleteCandidate: (thread: ChatThreadRead | null) => void;
  onCancelDelete: () => void;
  onConfirmDelete: () => void;
  onNavigateToSource?: (messageId: string) => void;
  onSubmitCase?: (data: CaseIntakeSubmission) => void;
  onClearQueryError?: () => void;
  onRetryQuery?: () => void;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
}

