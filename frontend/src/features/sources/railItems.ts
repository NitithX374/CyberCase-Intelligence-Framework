import type { CaseSourceRead } from "@/lib/api/types";
import type { FollowupAnswer } from "@/features/citations/types";

export type RailItem =
  | { id: string; kind: "file"; documentId: string; source: CaseSourceRead }
  | { id: string; kind: "narrative"; source: CaseSourceRead }
  | { id: string; kind: "followup_answer"; followup: FollowupAnswer };

export interface RailGroup {
  label: string;
  items: RailItem[];
}

export function isTurnedOff(source: CaseSourceRead): boolean {
  return source.deactivated_at != null;
}

function currentReadings(sources: CaseSourceRead[]): CaseSourceRead[] {
  const newest = new Map<string, CaseSourceRead>();
  for (const source of sources) {
    if (!source.document_id) continue;
    const kept = newest.get(source.document_id);
    if (!kept || Date.parse(source.created_at) >= Date.parse(kept.created_at)) {
      newest.set(source.document_id, source);
    }
  }
  return sources.filter(
    (source) => !source.document_id || newest.get(source.document_id) === source,
  );
}

function sourceItems(sources: CaseSourceRead[], kind: "file" | "narrative"): RailItem[] {
  return sources.flatMap((source): RailItem[] => {
    if (kind === "file" && source.source_kind === "document" && source.document_id) {
      return [{ id: source.document_id, kind: "file", documentId: source.document_id, source }];
    }
    if (kind === "narrative" && source.source_kind === "narrative") {
      return [{ id: source.id, kind: "narrative", source }];
    }
    return [];
  });
}

export function railGroups(sources: CaseSourceRead[], followups: FollowupAnswer[]): RailGroup[] {
  const current = currentReadings(sources);
  const on = current.filter((source) => !isTurnedOff(source));
  const off = current.filter(isTurnedOff);
  return [
    { label: "Files", items: sourceItems(on, "file") },
    { label: "Case narrative", items: sourceItems(on, "narrative") },
    {
      label: "Follow-up answers",
      items: followups.map((followup): RailItem => ({
        id: followup.qaId,
        kind: "followup_answer",
        followup,
      })),
    },
    {
      label: "Turned off",
      items: [...sourceItems(off, "file"), ...sourceItems(off, "narrative")],
    },
  ].filter((group) => group.items.length > 0);
}

export function itemTitle(item: RailItem): string {
  if (item.kind === "file") return item.source.filename ?? "Untitled file";
  if (item.kind === "followup_answer")
    return firstLine(item.followup.question || item.followup.answer);
  return firstLine(item.source.exact_text);
}

export function firstLine(text: string): string {
  const line = text.trim().split("\n")[0] ?? "";
  return line.length > 80 ? `${line.slice(0, 80)}…` : line || "Untitled source";
}
