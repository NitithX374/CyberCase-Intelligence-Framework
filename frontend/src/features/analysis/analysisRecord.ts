import type { CaseAnalysisResultRead } from "@/lib/api";
import type { FollowupAnswer } from "@/features/sources/types";
import { asArray, asRecord, asString } from "@/lib/parse";

export function analysisFollowups(result: CaseAnalysisResultRead): FollowupAnswer[] {
  const snapshot = asRecord(result.external_context_json?.followup_history);
  return asArray(snapshot?.items).flatMap((raw) => {
    const item = asRecord(raw);
    const qaId = asString(item?.qa_id);
    const answer = asString(item?.answer);
    return qaId && answer ? [{ qaId, question: asString(item?.question), answer }] : [];
  });
}

export function analysisSourceIds(result: CaseAnalysisResultRead): string[] {
  const read = asRecord(result.external_context_json?.sources_read);
  return asArray(read?.source_ids).map(asString).filter(Boolean);
}
