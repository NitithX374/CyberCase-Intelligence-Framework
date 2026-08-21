import type { FormEvent } from "react";

import type {
  RunPhase,
  WorkspaceRouteView,
  WorkspaceView,
} from "@/components/common/types";
import type { CaseStateInspectorUpdate } from "@/components/conversation/CaseStateInspector";
import type {
  ChatMessageAction,
  ChatThreadRead,
  PersistedChatMessage,
  ThreadStatus,
} from "@/lib/api";

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
  latestExtraction: ReturnType<typeof import("@/lib/chat-extraction").latestChatExtractionForMessages>;
  hasValidatedExtraction: boolean;
  messages: PersistedChatMessage[];
  caseUpdates: CaseStateInspectorUpdate[];
  deleteCandidate: ChatThreadRead | null;
  selectedCaseUpdateOrdinal: number | null;
  isCaseInspectorOpen: boolean;
  onSelectThread: (threadId: string) => void;
  onNewChat: () => void;
  onRequestDelete: (thread: ChatThreadRead) => void;
  onViewChange: (view: WorkspaceView) => void;
  onInputChange: (value: string) => void;
  onPostAnswerActionChange: (action: ChatMessageAction) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onSelectMessageOrdinal: (ordinal: number) => void;
  onSetDeleteCandidate: (thread: ChatThreadRead | null) => void;
  onCancelDelete: () => void;
  onConfirmDelete: () => void;
  onSelectCaseUpdateOrdinal: (ordinal: number | null) => void;
  onSetCaseInspectorOpen: (open: boolean) => void;
}
