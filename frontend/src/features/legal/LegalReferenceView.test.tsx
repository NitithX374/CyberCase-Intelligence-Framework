import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LegalReferenceView } from "./LegalReferenceView";
import type { CaseAnalysisResultRead } from "@/lib/api";

const ACCESS_SECTION = "พระราชบัญญัติว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ พ.ศ. 2550 มาตรา 5";
const FRAUD_SECTION = "ประมวลกฎหมายอาญา มาตรา 341";

function analysis(externalContext: Record<string, unknown>): CaseAnalysisResultRead {
  return {
    id: "analysis-1",
    case_id: "case-1",
    source_revision: 1,
    schema_version: "case_analysis_trace_v1",
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
  it("shows no provision until the reader accepts the notice", () => {
    render(<LegalReferenceView analysisResult={withProvisions()} onDecline={vi.fn()} />);

    const notice = screen.getByRole("dialog");
    expect(
      within(notice).getByRole("heading", { name: "โปรดอ่านก่อนดูข้อมูลกฎหมาย" }),
    ).toBeInTheDocument();
    expect(notice).toHaveTextContent("ไม่ใช่ความเห็นทางกฎหมาย");
    expect(screen.queryByRole("heading", { name: ACCESS_SECTION })).not.toBeInTheDocument();

    fireEvent.click(within(notice).getByRole("button", { name: "รับทราบ" }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: ACCESS_SECTION })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: FRAUD_SECTION })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Legal references" })).toHaveTextContent(
      "รายการอ้างอิงตัวบทที่อาจเกี่ยวข้อง ไม่ใช่ความเห็นทางกฎหมาย",
    );
  });

  it("leaves the page when the reader declines", () => {
    const onDecline = vi.fn();
    render(<LegalReferenceView analysisResult={withProvisions()} onDecline={onDecline} />);

    fireEvent.click(within(screen.getByRole("dialog")).getByRole("button", { name: "ยกเลิก" }));

    expect(onDecline).toHaveBeenCalledOnce();
    expect(screen.queryByRole("heading", { name: ACCESS_SECTION })).not.toBeInTheDocument();
  });

  it("links only to web addresses the provider gave", () => {
    render(<LegalReferenceView analysisResult={withProvisions()} onDecline={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "รับทราบ" }));

    expect(
      screen.getByRole("link", { name: `Open ${ACCESS_SECTION} at the source` }),
    ).toHaveAttribute("href", "https://example.go.th/computer-crime-act#5");
    expect(
      screen.queryByRole("link", { name: `Open ${FRAUD_SECTION} at the source` }),
    ).not.toBeInTheDocument();
  });

  it("folds a long provision behind Full text", () => {
    render(<LegalReferenceView analysisResult={withProvisions()} onDecline={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "รับทราบ" }));

    const toggle = screen.getByRole("button", { name: "Full text" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
  });

  it("says why there is nothing when the case needed no ATT&CK context", () => {
    render(
      <LegalReferenceView
        analysisResult={analysis({ technical_augmentation: { status: "not_applicable" } })}
        onDecline={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "No legal references" })).toBeInTheDocument();
    expect(screen.getByText(/judged not to need it/)).toBeInTheDocument();
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
        onDecline={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "No provisions found" })).toBeInTheDocument();
    expect(screen.getByText("บริการอ้างอิงตัวบทใช้เวลานานเกินกำหนด")).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("waits for an analysis before looking anything up", () => {
    render(<LegalReferenceView analysisResult={null} onDecline={vi.fn()} />);

    expect(screen.getByRole("heading", { name: "Not analyzed yet" })).toBeInTheDocument();
  });
});
