import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TechnicalContextView } from "@/components/technical/TechnicalContextView";
import type { PersistedChatMessage } from "@/lib/api";

describe("TechnicalContextView", () => {
  const sampleMessages: PersistedChatMessage[] = [
    {
      id: "msg-1",
      thread_id: "thread-1",
      ordinal: 1,
      role: "user",
      content: "คนร้ายเจาะระบบผ่านช่องโหว่ IIS Web Server",
      retrieval_context_id: null,
      metadata_json: {},
      created_at: "2026-03-10T08:00:00Z",
    },
    {
      id: "msg-2",
      thread_id: "thread-1",
      ordinal: 2,
      role: "assistant",
      content: "วิเคราะห์...",
      retrieval_context_id: "ret-1",
      metadata_json: {
        analysis_kind: "grounded_main_analysis",
        mitre_table: [
          {
            technique_id: "T1190",
            name: "Exploit Public-Facing Application",
            tactic: "Initial Access",
            description: "Abuse of a public-facing application to gain access.",
            reason: "คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server",
          },
        ],
        analysis_trace: {
          version: "analysis_trace_v2",
          claims: [
            {
              claim_id: "c1",
              text: "คนร้ายโจมตีผ่านช่องโหว่ IIS",
              claim_type: "event_progression",
              epistemic_status: "reported",
              source_message_ids: ["msg-1"],
            },
          ],
          mitre_associations: [
            {
              association_id: "assoc-1",
              technique_id: "T1190",
              claim_ids: ["c1"],
              reason: "คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server",
              status: "candidate",
              support_role: "external_knowledge",
            },
          ],
        },
      },
      created_at: "2026-03-10T08:01:00Z",
    },
  ];

  it("renders flattened MITRE notes with quiet external reference notice and case basis", () => {
    render(<TechnicalContextView messages={sampleMessages} />);

    expect(screen.getByText("MITRE ATT&CK Context")).toBeInTheDocument();
    expect(screen.getByText("External technical reference · not case evidence")).toBeInTheDocument();

    // Technique details
    expect(screen.getByText("T1190")).toBeInTheDocument();
    expect(screen.getByText("Exploit Public-Facing Application")).toBeInTheDocument();
    expect(screen.getByText("Initial Access")).toBeInTheDocument();
    expect(screen.getByText("ความหมายโดยย่อ")).toBeInTheDocument();
    expect(screen.getByText("เหตุผลที่เกี่ยวข้องกับคดี")).toBeInTheDocument();
    expect(screen.getByText("คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server")).toBeInTheDocument();

    // Case basis source button
    const sourceBtn = screen.getByRole("button", { name: /Source — Initial case description/i });
    expect(sourceBtn).toBeInTheDocument();

    // Click source button to open popover
    fireEvent.click(sourceBtn);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText(/SOURCE FROM CASE/i)).toBeInTheDocument();
    expect(screen.getByText("คนร้ายเจาะระบบผ่านช่องโหว่ IIS Web Server")).toBeInTheDocument();
  });

  it("renders empty state when no MITRE context exists", () => {
    render(<TechnicalContextView messages={[]} />);
    expect(
      screen.getByText(/No relevant MITRE ATT&CK context is currently available/i),
    ).toBeInTheDocument();
  });
});
