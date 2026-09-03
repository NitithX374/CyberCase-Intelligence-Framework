import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useRef, useState } from "react";
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
  displayContent: "On May 12, 2023, an unauthorized user executed PowerShell script Updater.exe via scheduled task.",
  exactQuote: "an unauthorized user executed PowerShell script Updater.exe",
  documentId: "DOC-1",
  filename: "incident-report.pdf",
  pageNumbers: [4],
  evidencePages: [{
    pageNumber: 4,
    text: "On May 12, 2023, an unauthorized user executed PowerShell script Updater.exe via scheduled task.",
    exactQuote: "an unauthorized user executed PowerShell script Updater.exe",
  }],
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
    expect(screen.getByText("incident-report.pdf")).toBeInTheDocument();
    expect(screen.getByRole("dialog")).toHaveTextContent(
      "On May 12, 2023, an unauthorized user executed PowerShell script Updater.exe via scheduled task.",
    );
    expect(screen.getByText("an unauthorized user executed PowerShell script Updater.exe").tagName).toBe("MARK");
    expect(screen.getByText("Page 4")).toBeInTheDocument();

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

  it("renders each cited page separately and restores focus after Escape", () => {
    function Harness() {
      const [open, setOpen] = useState(false);
      const anchorRef = useRef<HTMLButtonElement>(null);
      const sourceRef = {
        ...mockSourceRef,
        pageNumbers: [4, 5],
        evidencePages: [
          { pageNumber: 4, text: "Page 4 evidence.", exactQuote: "Page 4 evidence." },
          { pageNumber: 5, text: "Page 5 evidence.", exactQuote: "Page 5 evidence." },
        ],
      };
      return (
        <>
          <button ref={anchorRef} type="button" onClick={() => setOpen(true)}>Open evidence</button>
          {open && (
            <SourceEvidencePopover
              sourceRef={sourceRef}
              anchorElement={anchorRef.current}
              onClose={() => setOpen(false)}
            />
          )}
        </>
      );
    }

    render(<Harness />);
    const anchor = screen.getByRole("button", { name: "Open evidence" });
    fireEvent.click(anchor);
    expect(screen.getByText("Page 4")).toBeInTheDocument();
    expect(screen.getByText("Page 5")).toBeInTheDocument();
    expect(screen.getByText("Page 4 evidence.").tagName).toBe("MARK");
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(anchor).toHaveFocus();
  });

  it("highlights every occurrence of the validated quote on a page", () => {
    const anchor = document.createElement("button");
    document.body.appendChild(anchor);
    const sourceRef = {
      ...mockSourceRef,
      evidencePages: [{
        pageNumber: 4,
        text: "The same phrase appears; the same phrase is repeated.",
        exactQuote: "same phrase",
      }],
    };

    render(
      <SourceEvidencePopover
        sourceRef={sourceRef}
        anchorElement={anchor}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getAllByText("same phrase")).toHaveLength(2);
    expect(screen.getAllByText("same phrase").every((element) => element.tagName === "MARK")).toBe(true);
  });

  it("uses a readable bottom-sheet layout on mobile", () => {
    const originalWidth = window.innerWidth;
    Object.defineProperty(window, "innerWidth", { configurable: true, value: 375 });
    const anchor = document.createElement("button");
    document.body.appendChild(anchor);

    render(
      <SourceEvidencePopover
        sourceRef={mockSourceRef}
        anchorElement={anchor}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByRole("dialog").className).toContain("inset-x-3");
    expect(screen.getByRole("dialog").className).toContain("bottom-4");
    expect(document.querySelector(".backdrop-blur-\\[2px\\]")).toBeInTheDocument();
    Object.defineProperty(window, "innerWidth", { configurable: true, value: originalWidth });
  });
});
