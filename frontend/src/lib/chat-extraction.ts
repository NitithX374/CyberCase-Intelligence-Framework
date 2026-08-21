import type { PersistedChatMessage } from "@/lib/api";
import {
  baselineCandidateSchema,
  baselineFailureSchema,
  type ChatBaselineExtraction,
  type ChatBaselineExtractionFailure,
  type ChatExtraction,
} from "@/lib/metadata-schemas";

export function chatBaselineExtractionForMessage(
  message: PersistedChatMessage,
): ChatBaselineExtraction | ChatBaselineExtractionFailure | null {
  if (message.role !== "assistant") return null;
  const raw = message.metadata_json.chat_extraction;
  const failure = baselineFailureSchema.safeParse(raw);
  if (failure.success) return failure.data;

  const candidate = baselineCandidateSchema.safeParse(raw);
  if (!candidate.success || !hasValidReferences(candidate.data)) return null;

  const { missing_information: missingInformation, ...parsedCandidate } =
    candidate.data;
  return {
    ...parsedCandidate,
    ...(missingInformation?.length
      ? { missing_information: missingInformation }
      : {}),
  };
}

export function chatExtractionForMessage(
  message: PersistedChatMessage,
): ChatExtraction | null {
  return chatBaselineExtractionForMessage(message);
}

export function latestChatExtractionForMessages(
  messages: PersistedChatMessage[],
): ChatExtraction | null {
  for (const message of [...messages].sort(
    (left, right) => right.ordinal - left.ordinal,
  )) {
    const extraction = chatExtractionForMessage(message);
    if (extraction) return extraction;
  }
  return null;
}

function hasValidReferences(candidate: ChatBaselineExtraction): boolean {
  const entityIds = new Set(candidate.entities.map((entity) => entity.entity_id));
  const evidenceIds = new Set(candidate.evidence.map((item) => item.evidence_id));
  const timelineIds = new Set(candidate.timeline.map((event) => event.event_id));
  const relationshipIds = new Set(
    candidate.relationships.map((relationship) => relationship.relationship_id),
  );
  const semanticEdges = new Set(
    candidate.relationships.map(
      ({ subject_entity_id, predicate, object_entity_id }) =>
        `${subject_entity_id}\u0000${predicate}\u0000${object_entity_id}`,
    ),
  );

  if (
    entityIds.size !== candidate.entities.length ||
    evidenceIds.size !== candidate.evidence.length ||
    timelineIds.size !== candidate.timeline.length ||
    relationshipIds.size !== candidate.relationships.length ||
    semanticEdges.size !== candidate.relationships.length
  ) {
    return false;
  }

  return (
    candidate.timeline.every((event) =>
      event.evidence_ids.every((id) => evidenceIds.has(id)),
    ) &&
    candidate.relationships.every(
      ({ subject_entity_id, object_entity_id }) =>
        subject_entity_id !== object_entity_id &&
        entityIds.has(subject_entity_id) &&
        entityIds.has(object_entity_id),
    )
  );
}
