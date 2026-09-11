import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseClarificationSection } from "@/components/overview/CaseClarificationSection";
import type { CaseClarificationRead } from "@/lib/api";

const clarification: CaseClarificationRead = {
  id: "clarification-1",
  case_id: "case-1",
  origin_analysis_result_id: "analysis-1",
  origin_snapshot_id: "snapshot-1",
  gap_key: "topic:incident-time",
  gap_id: "G-01",
  topic: "Incident time",
  question: "When was the incident reported?",
  metadata_json: {},
  state: "pending",
  answer_evidence_source_id: null,
  question_message_id: null,
  answer_message_id: null,
  answer_fingerprint: null,
  answered_at: null,
  created_at: "2026-09-10T01:00:00Z",
  updated_at: "2026-09-10T01:00:00Z",
};

describe("CaseClarificationSection", () => {
  it("answers a pending clarification without opening Chat", () => {
    const onAnswer = vi.fn();
    render(
      <CaseClarificationSection
        clarifications={[clarification]}
        submittingId={null}
        onAnswer={onAnswer}
      />,
    );

    fireEvent.change(screen.getByRole("textbox", { name: "Answer: Incident time" }), {
      target: { value: "The incident was reported at 09:00." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit answer and re-analyze" }));

    expect(onAnswer).toHaveBeenCalledWith(
      "clarification-1",
      "The incident was reported at 09:00.",
    );
  });
});
