import { describe, expect, it } from "vitest";

import { caseUpdateForMessage } from "@/lib/case-update";
import type { PersistedChatMessage } from "@/lib/api";

function message(
  ordinal: number,
  metadata_json: Record<string, unknown>,
): PersistedChatMessage {
  return {
    id: `message-${ordinal}`,
    thread_id: "thread-1",
    ordinal,
    role: "assistant",
    content: "Analysis",
    retrieval_context_id: null,
    metadata_json,
    created_at: "2026-08-20T00:00:00Z",
  };
}

function updatedProjection(): Record<string, unknown> {
  return {
    version: "case_update_v1",
    status: "updated",
    parent_case_state_version_id: "version-3",
    parent_version: 3,
    child_case_state_version_id: "version-4",
    child_version: 4,
    delta: {
      changes: [
        {
          target_type: "evidence",
          target_id: "E-010",
          field: null,
          old_value: null,
          new_value: {
            evidence_id: "E-010",
            title: "Authentication log",
            description: "ADMIN01 logged in.",
          },
        },
        {
          target_type: "relationship",
          target_id: "REL-004",
          field: "status",
          old_value: "not_established",
          new_value: "suspected",
        },
      ],
    },
  };
}

describe("caseUpdateForMessage", () => {
  it("projects only deterministic ADD and MODIFY operations", () => {
    const updateMessage = message(4, { case_update: updatedProjection() });

    const update = caseUpdateForMessage(updateMessage, [updateMessage]);

    expect(update).toMatchObject({
      status: "updated",
      parentVersion: 3,
      childVersion: 4,
      added: [
        {
          targetType: "evidence",
          targetId: "E-010",
          summary: "E-010 · Authentication log",
        },
      ],
      changed: [
        {
          targetType: "relationship",
          targetId: "REL-004",
          field: "status",
          oldValue: "not_established",
          newValue: "suspected",
        },
      ],
    });
  });

  it("uses the latest completed Gap Analysis without inferring resolution", () => {
    const olderGap = message(2, {
      chat_followup: {
        gap_analysis: {
          status: "completed",
          gaps: [
            {
              topic: "Credential source",
              description: "The credential source is not reported.",
              status: "NOT_PROVIDED",
              priority: "high",
            },
          ],
        },
      },
    });
    const failedNewerGap = message(3, {
      chat_followup: {
        gap_analysis: { status: "failed", gaps: [] },
      },
    });
    const updateMessage = message(4, { case_update: updatedProjection() });

    const update = caseUpdateForMessage(updateMessage, [
      olderGap,
      failedNewerGap,
      updateMessage,
    ]);

    expect(update?.currentUnresolvedInformation).toEqual([
      {
        topic: "Credential source",
        description: "The credential source is not reported.",
        status: "NOT_PROVIDED",
        priority: "high",
      },
    ]);
  });

  it("preserves an explicit no-change result without inventing a child", () => {
    const updateMessage = message(4, {
      case_update: {
        version: "case_update_v1",
        status: "no_change",
        parent_case_state_version_id: "version-2",
        parent_version: 2,
        child_case_state_version_id: null,
        child_version: null,
        delta: { changes: [] },
      },
    });

    const update = caseUpdateForMessage(updateMessage, [updateMessage]);

    expect(update).toMatchObject({
      status: "no_change",
      parentVersion: 2,
      childVersion: null,
      added: [],
      changed: [],
    });
  });

  it("hides malformed or removal-like projections", () => {
    const invalid = updatedProjection();
    invalid.delta = {
      changes: [
        {
          target_type: "evidence",
          target_id: "E-010",
          field: null,
          old_value: { title: "Old" },
          new_value: null,
        },
      ],
    };
    const updateMessage = message(4, { case_update: invalid });

    expect(caseUpdateForMessage(updateMessage, [updateMessage])).toBeNull();
  });
});
