import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ChatMessageRead } from "@/lib/api";
import { mockNativeDialog } from "@/test/mockNativeDialog";
import { mergeCaseSourceRows } from "./followupSources";
import { parseCaseSources, sourceRefs } from "./sourceRefs";
import { SourceDrawer } from "./SourceDrawer";

mockNativeDialog();

const caseId = "22222222-2222-4222-8222-222222222222";

const messages: ChatMessageRead[] = [
  {
    id: "question-1",
    case_id: caseId,
    ordinal: 1,
    role: "assistant",
    content: "Was a warrant issued?",
    message_kind: "followup_question",
    gap_key: "arrest_warrant",
    analysis_result_id: null,
    metadata_json: {},
    created_at: "2026-09-24T13:47:53Z",
  },
  {
    id: "answer-1",
    case_id: caseId,
    ordinal: 2,
    role: "user",
    content: "No.",
    message_kind: "followup_answer",
    analysis_result_id: null,
    in_reply_to_message_id: "question-1",
    metadata_json: {},
    created_at: "2026-09-24T13:48:48Z",
  },
];

describe("SourceDrawer", () => {
  it("shows a follow-up answer with the question it answers", () => {
    const [answer] = sourceRefs(["QA-01"], [], parseCaseSources(mergeCaseSourceRows([], messages)));
    const anchor = document.body.appendChild(document.createElement("button"));

    render(<SourceDrawer sourceRef={answer} anchorElement={anchor} onClose={vi.fn()} />);

    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent(
      /^Source: Follow-up answer #1$/,
    );
    const terms = screen.getAllByRole("term").map((term) => term.textContent);
    const definitions = screen.getAllByRole("definition").map((item) => item.textContent);
    expect(terms).toEqual(["Question", "Answer"]);
    expect(definitions).toEqual(["Was a warrant issued?", "No."]);
  });
});
