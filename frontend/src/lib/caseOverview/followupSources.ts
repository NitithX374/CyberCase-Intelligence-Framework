import type { CaseSourceRead, ChatMessageRead } from "@/lib/api";

export function mergeCaseSourceRows(
  caseSources: CaseSourceRead[],
  messages: ChatMessageRead[],
): CaseSourceRead[] {
  const followupSources = buildFollowupSources(messages);
  const existingIds = new Set(caseSources.map((source) => source.id));
  return [
    ...caseSources,
    ...followupSources.filter((source) => !existingIds.has(source.id)),
  ];
}

function buildFollowupSources(messages: ChatMessageRead[]): CaseSourceRead[] {
  const ordered = [...messages].sort((left, right) => left.ordinal - right.ordinal);
  const replies = new Map(
    ordered
      .filter(
        (message) =>
          message.message_kind === "followup_answer" && message.in_reply_to_message_id,
      )
      .map((message) => [message.in_reply_to_message_id!, message]),
  );
  const questions = ordered.filter((message) => Boolean(message.gap_key));

  return questions.flatMap((question, index) => {
    const answer = replies.get(question.id);
    if (!answer?.content.trim()) return [];
    return [
      {
        id: followupSourceId(index + 1),
        case_id: answer.case_id,
        source_kind: "followup_answer",
        document_id: null,
        origin_message_id: answer.id,
        exact_text: answer.content,
        provenance_json: {
          origin: "case_followup",
          gap_key: question.gap_key,
        },
        source_metadata_json: {
          question: question.content,
        },
        created_at: answer.created_at,
        archived_at: null,
      },
    ];
  });
}

function followupSourceId(index: number): string {
  return `QA-${String(index).padStart(2, "0")}`;
}
