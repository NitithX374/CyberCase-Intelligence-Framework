import type { CaseAnalysisClaim, ChatAnswerUnit } from "@/lib/api/types";
import type { CaseSourceRef, SourceMessageRef } from "@/features/citations/types";
import { claimRefs } from "@/features/citations/sourceRefs";
import {
  checkedSources,
  unconfirmedStatuses,
  type UnconfirmedStatus,
} from "@/features/citations/unconfirmed";

export interface AnalysisSourceReference {
  role: "supporting" | "conflicting";
  source: SourceMessageRef;
}

export interface ReferenceList {
  references: AnalysisSourceReference[];
  unconfirmed: UnconfirmedStatus[];
}

type CitedItem = Parameters<typeof claimRefs>[0] & { unconfirmed: UnconfirmedStatus[] };

export function claimItem(claim: CaseAnalysisClaim): CitedItem {
  return { ...claim, unconfirmed: unconfirmedStatuses([claim.epistemic_status]) };
}

export function unitItem(unit: ChatAnswerUnit, statuses: Map<string, string>): CitedItem {
  return {
    ...unit,
    unconfirmed: unconfirmedStatuses((unit.claim_ids ?? []).map((id) => statuses.get(id))),
  };
}

export function sourceReferences(items: CitedItem[], sources: CaseSourceRef[]): ReferenceList {
  const references = items.flatMap((item) => {
    const cited = claimRefs(item, sources);
    return [
      ...checkedSources(cited.supporting, item.unconfirmed.length > 0).map((source) => ({
        role: "supporting" as const,
        source,
      })),
      ...cited.contradicting.map((source) => ({ role: "conflicting" as const, source })),
    ];
  });
  const unique = new Map<string, AnalysisSourceReference>();
  for (const reference of references) {
    const key = [reference.role, reference.source.id, reference.source.pageNumbers.join(",")].join(
      ":",
    );
    if (!unique.has(key)) {
      unique.set(key, reference);
    }
  }
  return {
    references: [...unique.values()].slice(0, 12),
    unconfirmed: unconfirmedStatuses(items.flatMap((item) => item.unconfirmed)),
  };
}
