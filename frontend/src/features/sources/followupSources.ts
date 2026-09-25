import type { ChatMessageRead } from "@/lib/api";
import type { FollowupAnswer } from "./types";

export function chatFollowups(messages: ChatMessageRead[]): FollowupAnswer[] {
  const answers = new Map(
    messages.flatMap((message) =>
      message.message_kind === "followup_answer" && message.qa_id
        ? [[message.qa_id, message.content] as const]
        : [],
    ),
  );
  return messages.flatMap((message) => {
    if (message.message_kind !== "followup_question" || !message.qa_id) return [];
    const answer = answers.get(message.qa_id);
    return answer?.trim() ? [{ qaId: message.qa_id, question: message.content, answer }] : [];
  });
}
