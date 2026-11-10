import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LegalReferenceView } from "@/features/legal/LegalReferenceView";
import type { CaseAnalysisResultRead } from "@/lib/api/types";

const ACCESS_SECTION = "พระราชบัญญัติว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ พ.ศ. 2550 มาตรา 5";
const FRAUD_SECTION = "ประมวลกฎหมายอาญา มาตรา 341";

function analysis(externalContext: Record<string, unknown>): CaseAnalysisResultRead {
  return {
    id: "analysis-1",
    case_id: "case-1",
    source_revision: 1,
    status: "validated",
    summary: "",
    trace_json: null,
    retrieval_context_id: null,
    pipeline_config: {},
    external_context_json: externalContext,
    created_at: "2026-09-10T00:00:00Z",
    freshness: "current",
  };
}

function withProvisions() {
  return analysis({
    technical_augmentation: { status: "retrieved_with_matches" },
    legal_relevance: {
      provisions: [
        {
          citation: ACCESS_SECTION,
          title: "พระราชบัญญัติว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ พ.ศ. 2550",
          text: "ผู้ใดเข้าถึงโดยมิชอบซึ่งระบบคอมพิวเตอร์ที่มีมาตรการป้องกันการเข้าถึงโดยเฉพาะ",
          url: "https://example.go.th/computer-crime-act#5",
          score: 0.82,
        },
        {
          citation: FRAUD_SECTION,
          title: "ประมวลกฎหมายอาญา",
          text: "ผู้ใดโดยทุจริต หลอกลวงผู้อื่นด้วยการแสดงข้อความอันเป็นเท็จ ".repeat(12),
          url: "javascript:alert(1)",
          score: 0.64,
        },
      ],
      provider: "iapp-thai-legal",
      query_sent: "คนร้ายเข้าถึงบัญชีธนาคารออนไลน์ของผู้เสียหายแล้วโอนเงินออก",
      degraded: "",
      disclaimer: "รายการอ้างอิงตัวบทที่อาจเกี่ยวข้อง ไม่ใช่ความเห็นทางกฎหมาย",
    },
  });
}

describe("LegalReferenceView", () => {
  it("shows the provisions and the disclaimer at once, with no notice to accept", () => {
    render(<LegalReferenceView analysisResult={withProvisions()} />);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "รับทราบ" })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: ACCESS_SECTION })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: FRAUD_SECTION })).toBeInTheDocument();
    const region = screen.getByRole("region", { name: "Legal references" });
    expect(region).toHaveTextContent("รายการอ้างอิงตัวบทที่อาจเกี่ยวข้อง ไม่ใช่ความเห็นทางกฎหมาย");
    expect(within(region).getByRole("heading", { name: "Provisions" })).toBeInTheDocument();
  });

  it("links only to web addresses the provider gave", () => {
    render(<LegalReferenceView analysisResult={withProvisions()} />);

    expect(
      screen.getByRole("link", { name: `Open ${ACCESS_SECTION} at the source` }),
    ).toHaveAttribute("href", "https://example.go.th/computer-crime-act#5");
    expect(
      screen.queryByRole("link", { name: `Open ${FRAUD_SECTION} at the source` }),
    ).not.toBeInTheDocument();
  });

  it("folds a long provision behind Full text", () => {
    render(<LegalReferenceView analysisResult={withProvisions()} />);

    const toggle = screen.getByRole("button", { name: "Full text" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
  });

  it("says what was searched, folded under the provisions", () => {
    render(<LegalReferenceView analysisResult={withProvisions()} />);

    const searched = screen.getByText("What was searched").closest("details") as HTMLElement;
    expect(searched).not.toHaveAttribute("open");
    expect(searched).toHaveTextContent(
      "คนร้ายเข้าถึงบัญชีธนาคารออนไลน์ของผู้เสียหายแล้วโอนเงินออก",
    );
    expect(searched).toHaveTextContent("Searched on iapp-thai-legal");
  });

  it("says why there is nothing when the case needed no ATT&CK context", () => {
    render(
      <LegalReferenceView
        analysisResult={analysis({ technical_augmentation: { status: "not_applicable" } })}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Thai legal provisions: No legal references" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/This case had none/)).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("passes on the service's own reason when it found nothing", () => {
    render(
      <LegalReferenceView
        analysisResult={analysis({
          legal_relevance: {
            provisions: [],
            provider: "iapp-thai-legal",
            query_sent: "ข้อความ",
            degraded: "บริการอ้างอิงตัวบทใช้เวลานานเกินกำหนด",
            disclaimer: "",
          },
        })}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Thai legal provisions: No provisions found" }),
    ).toBeInTheDocument();
    expect(screen.getByText("บริการอ้างอิงตัวบทใช้เวลานานเกินกำหนด")).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("says when the analysis made no legal lookup", () => {
    render(<LegalReferenceView analysisResult={analysis({})} />);

    expect(
      screen.getByRole("heading", { name: "Thai legal provisions: No legal references" }),
    ).toBeInTheDocument();
    expect(screen.getByText("This analysis made no legal lookup.")).toBeInTheDocument();
  });

  it("waits for an analysis before looking anything up", () => {
    render(<LegalReferenceView analysisResult={null} />);

    expect(
      screen.getByRole("heading", { name: "Thai legal provisions: Not analyzed yet" }),
    ).toBeInTheDocument();
  });
});
