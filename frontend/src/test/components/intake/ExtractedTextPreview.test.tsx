import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtractedTextPreview } from "@/components/intake/ExtractedTextPreview";
import { intakeReadableText } from "@/lib/intake-readable-text";

describe("Intake document reading", () => {
  it("normalizes table cells and encoded markup without losing the original source", () => {
    const source = '<table><tr><td>ผู้กล่าวหา</td><td>A &amp; B</td></tr><tr><td>Date</td><td>12 May</td></tr></table>';
    expect(intakeReadableText(source)).toBe("ผู้กล่าวหา | A & B\nDate | 12 May");
    expect(intakeReadableText("&lt;p&gt;Statement &#65; &#x42;&lt;/p&gt;")).toBe("Statement A B");
    render(<ExtractedTextPreview text={source} label="Case narrative" />);
    expect(screen.getByLabelText("Case narrative text")).not.toHaveTextContent("<table>");
    fireEvent.click(screen.getByRole("tab", { name: "Raw Text" }));
    expect(screen.getByLabelText("Case narrative text").textContent).toBe(source);
  });

  it("keeps untrusted OCR content inert in both reading and raw modes", () => {
    const source = '<script>alert(1)</script><style>body{display:none}</style><p>Evidence</p><img src="https://invalid.test/a" onerror="alert(2)">';
    const { container } = render(<ExtractedTextPreview text={source} label="Case narrative" />);
    expect(screen.getByLabelText("Case narrative text")).toHaveTextContent("Evidence");
    expect(screen.getByLabelText("Case narrative text")).not.toHaveTextContent("alert(1)");
    fireEvent.click(screen.getByRole("tab", { name: "Raw Text" }));
    expect(container.querySelector("script, style, img, iframe")).toBeNull();
    expect(screen.getByLabelText("Case narrative text")).toHaveTextContent("onerror");
    expect(intakeReadableText("Value 3 < 5; unknown &#x110000; &custom;")).toBe("Value 3 < 5; unknown &#x110000; &custom;");
  });

  it("supports keyboard modes and opens the full text without truncating the source", () => {
    const text = `${"Long source paragraph.\n".repeat(120)}Final statement.`;
    const { container } = render(<ExtractedTextPreview text={text} label="Case narrative" />);
    const dialog = container.querySelector("dialog")!;
    dialog.showModal = () => dialog.setAttribute("open", "");
    dialog.close = () => dialog.removeAttribute("open");
    fireEvent.keyDown(screen.getByRole("tab", { name: "Overview" }), { key: "ArrowRight" });
    expect(screen.getByRole("tab", { name: "Extracted Text" })).toHaveAttribute("aria-selected", "true");
    const opener = screen.getByRole("button", { name: /View full extracted text/ });
    fireEvent.click(opener);
    expect(within(screen.getByRole("dialog")).getByText(/Final statement/)).toHaveTextContent("Final statement.");
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(opener).toHaveFocus();
  });
});
