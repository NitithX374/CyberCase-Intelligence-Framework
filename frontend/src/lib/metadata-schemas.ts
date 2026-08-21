import { z } from "zod";

const confidenceSchema = z.enum(["high", "medium", "low", "unknown"]);
const reportedStatusSchema = z.enum(["reported", "unknown", "not_confirmed"]);
const relationshipStatusSchema = z.enum([
  "reported",
  "suspected",
  "contradicted",
  "not_established",
]);
const sourceMessageIdsSchema = z.array(z.string());
const nonEmptyStringSchema = z.string().refine(
  (value) => value.trim().length > 0,
);

export const baselineEntitySchema = z.object({
  entity_id: nonEmptyStringSchema,
  name: nonEmptyStringSchema,
  entity_type: nonEmptyStringSchema,
  reported_role: nonEmptyStringSchema.nullable().optional().default(null),
  confidence: confidenceSchema,
  source_message_ids: sourceMessageIdsSchema,
});

export const baselineRelationshipSchema = z.object({
  relationship_id: nonEmptyStringSchema,
  subject_entity_id: nonEmptyStringSchema,
  predicate: z
    .string()
    .max(80)
    .regex(/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/),
  object_entity_id: nonEmptyStringSchema,
  statement: nonEmptyStringSchema,
  status: relationshipStatusSchema,
  confidence: confidenceSchema,
  source_message_ids: sourceMessageIdsSchema
    .min(1)
    .refine((items) => new Set(items).size === items.length),
});

export const baselineEvidenceSchema = z.object({
  evidence_id: nonEmptyStringSchema,
  title: nonEmptyStringSchema,
  description: nonEmptyStringSchema,
  artifact_type: nonEmptyStringSchema,
  status: reportedStatusSchema,
  confidence: confidenceSchema,
  source_type: z.literal("user_reported"),
  source_message_ids: sourceMessageIdsSchema,
});

export const baselineTimelineSchema = z.object({
  event_id: nonEmptyStringSchema,
  timestamp: nonEmptyStringSchema.nullable().optional().default(null),
  timestamp_text: nonEmptyStringSchema.nullable().optional().default(null),
  event: nonEmptyStringSchema,
  actors: z.array(z.string()),
  evidence_ids: z.array(z.string()),
  status: reportedStatusSchema,
  confidence: confidenceSchema,
  source_message_ids: sourceMessageIdsSchema,
});

export const baselineMissingInformationSchema = z.object({
  missing_id: nonEmptyStringSchema,
  description: nonEmptyStringSchema,
  importance: z.enum(["material", "important", "useful", "unknown"]),
  source_message_ids: sourceMessageIdsSchema,
});

const extractionMetadataSchema = z.object({
  version: z.string().optional(),
  mode: z.string().optional(),
  prompt_version: z.string().optional().default("baseline_extraction_prompt_v4"),
  provider: z.string().optional().default("unknown"),
  model: z.string().optional().default("unknown"),
  latency_ms: z.number().optional().default(0),
  input_tokens: z.number().nullable().optional().default(null),
  output_tokens: z.number().nullable().optional().default(null),
  source_message_ids: sourceMessageIdsSchema.optional().default([]),
  raw_response: z.string().nullable().optional().default(null),
});

export const baselineCandidateSchema = extractionMetadataSchema.extend({
  status: z.literal("candidate"),
  validation_status: z.literal("validated"),
  case_summary: z.string().optional(),
  entities: z.array(baselineEntitySchema).optional().default([]),
  relationships: z.array(baselineRelationshipSchema).optional().default([]),
  evidence: z.array(baselineEvidenceSchema).optional().default([]),
  timeline: z.array(baselineTimelineSchema).optional().default([]),
  missing_information: z.array(baselineMissingInformationSchema).optional(),
  warnings: z.array(z.string()).optional().default([]),
});

export const baselineFailureSchema = extractionMetadataSchema.extend({
  status: z.literal("failed"),
  validation_status: z.literal("failed"),
  failure_code: z.string(),
  failure_message: z
    .string()
    .optional()
    .default("The extraction did not produce a validated result."),
});

export const chatExtractionSchema = z.discriminatedUnion("status", [
  baselineCandidateSchema,
  baselineFailureSchema,
]);

export type ChatExtractionConfidence = z.infer<typeof confidenceSchema>;
export type ChatReportedStatus = z.infer<typeof reportedStatusSchema>;
export type ChatRelationshipStatus = z.infer<typeof relationshipStatusSchema>;
export type ChatBaselineEntity = z.infer<typeof baselineEntitySchema>;
export type ChatBaselineRelationship = z.infer<typeof baselineRelationshipSchema>;
export type ChatBaselineEvidence = z.infer<typeof baselineEvidenceSchema>;
export type ChatBaselineTimelineEvent = z.infer<typeof baselineTimelineSchema>;
export type ChatBaselineMissingInformation = z.infer<
  typeof baselineMissingInformationSchema
>;
export type ChatCaseState = {
  entities: ChatBaselineEntity[];
  relationships: ChatBaselineRelationship[];
  evidence: ChatBaselineEvidence[];
  timeline: ChatBaselineTimelineEvent[];
  warnings: string[];
};
export type ChatBaselineExtraction = z.infer<typeof baselineCandidateSchema>;
export type ChatBaselineExtractionFailure = z.infer<typeof baselineFailureSchema>;
export type ChatExtraction = z.infer<typeof chatExtractionSchema>;
