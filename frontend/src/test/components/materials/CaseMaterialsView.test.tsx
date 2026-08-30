import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import type { PersistedChatMessage } from "@/lib/api";

describe("CaseMaterialsView", () => {
  it("renders submitted case materials with numbered cards and type labels", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "รายละเอียดสำนวนคดีเริ่มต้น...",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "assistant",
        content: "วิเคราะห์...",
        retrieval_context_id: "ret-1",
        metadata_json: {},
        created_at: "2026-03-10T08:01:00Z",
      },
      {
        id: "msg-3",
        thread_id: "thread-1",
        ordinal: 3,
        role: "user",
        content: "คำตอบชี้แจงเพิ่มเติม...",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "clarification_answer" },
        created_at: "2026-03-10T08:05:00Z",
      },
    ];

    render(<CaseMaterialsView messages={messages} />);

    expect(screen.getByText(/CASE MATERIALS/i)).toBeInTheDocument();
    expect(screen.getByText(/Submitted Case Information/i)).toBeInTheDocument();
    expect(screen.getByText("01")).toBeInTheDocument();
    expect(screen.getByText(/Initial case description/i)).toBeInTheDocument();
    expect(screen.getByText("รายละเอียดสำนวนคดีเริ่มต้น...")).toBeInTheDocument();
    expect(screen.getByText("02")).toBeInTheDocument();
    expect(screen.getByText(/Clarification response/i)).toBeInTheDocument();
    expect(screen.getByText("คำตอบชี้แจงเพิ่มเติม...")).toBeInTheDocument();
  });

  it("renders empty state when no evidence messages exist", () => {
    render(<CaseMaterialsView messages={[]} />);
    expect(
      screen.getByText(/No case information has been submitted yet/i),
    ).toBeInTheDocument();
  });
});
