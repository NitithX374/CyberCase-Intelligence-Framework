import type { PersistedChatMessage } from "@/lib/api";

const targetTypes = [
  "fact",
  "entity",
  "relationship",
  "evidence",
  "timeline",
  "impact",
  "missing_information",
] as const;

type CaseUpdateTargetType = (typeof targetTypes)[number];
type Primitive = string | number | boolean;
type PrimitiveValue = Primitive | Primitive[];

export interface CaseUpdateAddedItem {
  targetType: CaseUpdateTargetType;
  targetId: string;
  summary: string;
}

export interface CaseUpdateModifiedItem {
  targetType: CaseUpdateTargetType;
  targetId: string;
  field: string;
  oldValue: PrimitiveValue;
  newValue: PrimitiveValue;
}

export interface CaseUpdateGap {
  topic: string;
  description: string;
  status: "NOT_PROVIDED" | "EXPLICITLY_UNKNOWN" | "AMBIGUOUS" | "CONFLICTING";
  priority: "high" | "medium" | "low";
  reason?: string;
  affects?: string;
  askable?: boolean;
}

export interface CaseUpdateView {
  status: "updated" | "no_change";
  parentVersion: number;
  childVersion: number | null;
  added: CaseUpdateAddedItem[];
  changed: CaseUpdateModifiedItem[];
  currentUnresolvedInformation: CaseUpdateGap[] | null;
}

export function caseUpdateForMessage(
  message: PersistedChatMessage,
  messages: PersistedChatMessage[],
): CaseUpdateView | null {
  const projection = parseProjection(message.metadata_json.case_update);
  if (!projection) return null;
  return {
    ...projection,
    currentUnresolvedInformation: latestValidatedGaps(messages, message.ordinal),
  };
}

function parseProjection(value: unknown): Omit<CaseUpdateView, "currentUnresolvedInformation"> | null {
  if (!isRecord(value) || value.version !== "case_update_v1") return null;
  if (value.status !== "updated" && value.status !== "no_change") return null;
  if (!isPositiveInteger(value.parent_version)) return null;
  if (!isNonEmptyString(value.parent_case_state_version_id)) return null;
  const childVersion = value.child_version;
  const childId = value.child_case_state_version_id;
  if (
    value.status === "updated" &&
    (!isPositiveInteger(childVersion) ||
      childVersion !== value.parent_version + 1 ||
      !isNonEmptyString(childId))
  ) {
    return null;
  }
  if (value.status === "no_change" && (childVersion !== null || childId !== null)) {
    return null;
  }
  const resolvedChildVersion =
    value.status === "updated" && isPositiveInteger(childVersion)
      ? childVersion
      : null;
  const delta = parseDelta(value.delta);
  if (!delta) return null;
  if (value.status === "no_change" && (delta.added.length || delta.changed.length)) {
    return null;
  }
  return {
    status: value.status,
    parentVersion: value.parent_version,
    childVersion: resolvedChildVersion,
    ...delta,
  };
}

function parseDelta(
  value: unknown,
): Pick<CaseUpdateView, "added" | "changed"> | null {
  if (!isRecord(value) || !Array.isArray(value.changes)) return null;
  const added: CaseUpdateAddedItem[] = [];
  const changed: CaseUpdateModifiedItem[] = [];
  for (const change of value.changes) {
    if (!isRecord(change) || !isTargetType(change.target_type)) return null;
    if (!isNonEmptyString(change.target_id)) return null;
    if (
      change.field === null &&
      change.old_value === null &&
      isRecord(change.new_value)
    ) {
      added.push({
        targetType: change.target_type,
        targetId: change.target_id,
        summary: addedItemSummary(
          change.target_type,
          change.target_id,
          change.new_value,
        ),
      });
      continue;
    }
    if (
      isNonEmptyString(change.field) &&
      isPrimitiveValue(change.old_value) &&
      isPrimitiveValue(change.new_value)
    ) {
      changed.push({
        targetType: change.target_type,
        targetId: change.target_id,
        field: change.field,
        oldValue: change.old_value,
        newValue: change.new_value,
      });
      continue;
    }
    return null;
  }
  return { added, changed };
}

export function latestValidatedGaps(
  messages: PersistedChatMessage[],
  maximumOrdinal: number,
): CaseUpdateGap[] | null {
  const candidates = [...messages]
    .filter(
      (message) =>
        message.role === "assistant" && message.ordinal <= maximumOrdinal,
    )
    .sort((left, right) => right.ordinal - left.ordinal);
  for (const candidate of candidates) {
    const followUp = candidate.metadata_json.chat_followup;
    if (!isRecord(followUp)) continue;
    const analysis = followUp.gap_analysis;
    if (!isRecord(analysis) || analysis.status !== "completed") continue;
    if (!Array.isArray(analysis.gaps)) continue;
    const gaps = analysis.gaps.map(parseGap);
    if (gaps.some((gap) => gap === null)) continue;
    return gaps.filter((gap): gap is CaseUpdateGap => gap !== null);
  }
  return null;
}

function parseGap(value: unknown): CaseUpdateGap | null {
  if (!isRecord(value)) return null;
  if (!isNonEmptyString(value.topic) || !isNonEmptyString(value.description)) {
    return null;
  }
  if (!isGapStatus(value.status) || !isGapPriority(value.priority)) return null;
  const gap: CaseUpdateGap = {
    topic: value.topic,
    description: value.description,
    status: value.status,
    priority: value.priority,
  };
  if (isNonEmptyString(value.reason)) {
    gap.reason = value.reason;
  }
  if (isNonEmptyString(value.affects)) {
    gap.affects = value.affects;
  }
  if (typeof value.askable === "boolean") {
    gap.askable = value.askable;
  }
  return gap;
}

function addedItemSummary(
  targetType: CaseUpdateTargetType,
  targetId: string,
  value: Record<string, unknown>,
): string {
  for (const field of ["statement", "name", "title", "event", "description"]) {
    if (isNonEmptyString(value[field])) return `${targetId} · ${value[field]}`;
  }
  return `${readableValue(targetType)} ${targetId}`;
}

export function formatCaseUpdateValue(value: PrimitiveValue): string {
  return Array.isArray(value) ? value.join(", ") : String(value);
}

export function readableValue(value: string): string {
  return value.replaceAll("_", " ");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isPositiveInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value > 0;
}

function isTargetType(value: unknown): value is CaseUpdateTargetType {
  return targetTypes.some((candidate) => candidate === value);
}

function isPrimitiveValue(value: unknown): value is PrimitiveValue {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return true;
  }
  return Array.isArray(value) && value.every(
    (item) =>
      typeof item === "string" ||
      typeof item === "number" ||
      typeof item === "boolean",
  );
}

function isGapStatus(value: unknown): value is CaseUpdateGap["status"] {
  return (
    value === "NOT_PROVIDED" ||
    value === "EXPLICITLY_UNKNOWN" ||
    value === "AMBIGUOUS" ||
    value === "CONFLICTING"
  );
}

function isGapPriority(value: unknown): value is CaseUpdateGap["priority"] {
  return value === "high" || value === "medium" || value === "low";
}
