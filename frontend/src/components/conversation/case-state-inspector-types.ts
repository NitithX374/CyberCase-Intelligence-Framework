import type { CaseUpdateGap, CaseUpdateView } from "@/lib/case-update";
import type { MitreCandidateView } from "@/lib/mitre-candidate";

export interface CaseStateInspectorUpdate {
  ordinal: number;
  update: CaseUpdateView;
  mitreCandidates?: MitreCandidateView[] | null;
}

export type InspectorTab = "delta" | "unresolved" | "mitre";

export interface CaseStateInspectorProps {
  updates: CaseStateInspectorUpdate[];
  selectedOrdinal: number | null;
  onSelectOrdinal: (ordinal: number) => void;
  isOpen: boolean;
  onClose: () => void;
}

export type UnresolvedGaps = CaseUpdateGap[] | null;
