import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SourceEvidencePopover } from "@/components/overview/SourceEvidencePopover";
import type { SourceMessageRef } from "@/lib/case-overview";

const mockSourceRef: SourceMessageRef = {
  id: "msg-1",
  ordinal: 1,
  label: "Case description",
  excerpt: "Initial report excerpt...",
  sourceType: "case_description",
  sourceTypeLabel: "Case description · รายละเอียดคดีเริ่มต้น",
  fullContent: "On May 12, 2023, an unauthorized user executed PowerShell script Updater.exe via scheduled task.",
};

describe("SourceEvidencePopover component", () => {
  it("renders the anchored source popover with friendly label and complete original message", () => {
    const anchor = document.createElement("button");
    document.body.appendChild(anchor);

    render(
      <SourceEvidencePopover
        sourceRef={mockSourceRef}
        anchorElement={anchor}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByText(/SOURCE FROM CASE/i)).toBeInTheDocument();
    expect(screen.getByText("Case description · รายละเอียดคดีเริ่มต้น")).toBeInTheDocument();
    expect(
      screen.getByText(
        "On May 12, 2023, an unauthorized user executed PowerShell script Updater.exe via scheduled task.",
      ),
    ).toBeInTheDocument();

    // Does NOT leak internal IDs
    expect(screen.queryByText("msg-1")).not.toBeInTheDocument();
  });

  it("calls onClose when close button is clicked", () => {
    const handleClose = vi.fn();
    const anchor = document.createElement("button");
    document.body.appendChild(anchor);

    render(
      <SourceEvidencePopover
        sourceRef={mockSourceRef}
        anchorElement={anchor}
        onClose={handleClose}
      />,
    );

    const closeBtn = screen.getByRole("button", { name: /Close source inspector/i });
    fireEvent.click(closeBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when Escape key is pressed", () => {
    const handleClose = vi.fn();
    const anchor = document.createElement("button");
    document.body.appendChild(anchor);

    render(
      <SourceEvidencePopover
        sourceRef={mockSourceRef}
        anchorElement={anchor}
        onClose={handleClose}
      />,
    );

    fireEvent.keyDown(document, { key: "Escape" });
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("calls onNavigateToSource and closes when View in Chat is clicked", () => {
    const handleClose = vi.fn();
    const handleNavigate = vi.fn();
    const anchor = document.createElement("button");
    document.body.appendChild(anchor);

    render(
      <SourceEvidencePopover
        sourceRef={mockSourceRef}
        anchorElement={anchor}
        onClose={handleClose}
        onNavigateToSource={handleNavigate}
      />,
    );

    const navBtn = screen.getByRole("button", { name: /View in Chat/i });
    fireEvent.click(navBtn);

    expect(handleNavigate).toHaveBeenCalledWith("msg-1");
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
