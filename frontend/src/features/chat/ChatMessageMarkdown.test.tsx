import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { ChatTranscript } from "./ChatTranscript";
import type { ChatMessageRead } from "@/lib/api";

describe("ChatMessageMarkdown", () => {
  it("renders headings, paragraphs, lists, bold text, blockquotes, inline code, and code blocks", () => {
    const markdown = `
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

This is a **bold paragraph** with \`inline code\`.

- Item 1
- Item 2

1. First
2. Second

> This is a blockquote

\`\`\`bash
powershell.exe -ExecutionPolicy Bypass
\`\`\`
    `.trim();

    render(<ChatMessageMarkdown content={markdown} />);

    expect(screen.getByRole("heading", { level: 1, name: "Heading 1" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "Heading 2" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 3, name: "Heading 3" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 4, name: "Heading 4" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 5, name: "Heading 5" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 6, name: "Heading 6" })).toBeInTheDocument();

    expect(screen.getByText("bold paragraph")).toBeInTheDocument();
    expect(screen.getByText("inline code")).toHaveClass("rounded", "bg-surface-hover", "text-ink");
    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("First")).toBeInTheDocument();
    expect(screen.getByText("This is a blockquote")).toBeInTheDocument();
    expect(screen.getByText("powershell.exe -ExecutionPolicy Bypass")).toBeInTheDocument();
    expect(screen.getByText("powershell.exe -ExecutionPolicy Bypass").closest("pre")).toHaveClass(
      "bg-primary",
      "text-ivory",
    );
  });

  it("renders GFM tables with responsive scroll container", () => {
    const markdown = `
| Technique | ID | Severity |
| --- | --- | --- |
| Command Execution | T1059 | High |
| Persistence | T1547 | Medium |
    `.trim();

    const { container } = render(<ChatMessageMarkdown content={markdown} />);

    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByText("Technique")).toBeInTheDocument();
    expect(screen.getByText("T1059")).toBeInTheDocument();

    const tableWrapper = container.querySelector(".overflow-x-auto");
    expect(tableWrapper).not.toBeNull();
    expect(tableWrapper).toHaveClass("bg-surface", "border-line");
  });

  it("does not render raw HTML elements or dangerouslySetInnerHTML", () => {
    const rawHtmlMarkdown = `
Hello <button id="unsafe-btn">Click me</button> <script>console.log('xss')</script>
    `.trim();

    const { container } = render(<ChatMessageMarkdown content={rawHtmlMarkdown} />);

    expect(container.querySelector("#unsafe-btn")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(screen.getByText(/Hello/)).toBeInTheDocument();
  });
});

describe("ChatTranscript Markdown vs Plain Text behavior", () => {
  it("renders assistant messages as Markdown and user messages as plain text", () => {
    const messages: ChatMessageRead[] = [
      {
        id: "msg-user",
        case_id: "caseChat-1",
        ordinal: 1,
        role: "user",
        content: "Check this **user message** with `code`.",
        message_kind: "conversation",
        analysis_result_id: null,
        metadata_json: {},
        created_at: "2026-07-29T12:00:00Z",
      },
      {
        id: "msg-assistant",
        case_id: "caseChat-1",
        ordinal: 2,
        role: "assistant",
        content: "Here is **assistant response** with `code`.",
        message_kind: "conversation",
        analysis_result_id: null,
        metadata_json: {},
        created_at: "2026-07-29T12:00:05Z",
      },
    ];

    render(<ChatTranscript messages={messages} isProcessing={false} />);

    expect(screen.getByText("Check this **user message** with `code`.")).toBeInTheDocument();

    const boldElement = screen.getByText("assistant response");
    expect(boldElement).toHaveClass("font-semibold");
    expect(boldElement.tagName).toBe("STRONG");

    const userMessage = screen.getByText("Check this **user message** with `code`.");
    expect(userMessage).toHaveClass("bg-surface-nested", "whitespace-pre-wrap");
    expect(userMessage.querySelector("strong")).toBeNull();
    expect(boldElement.closest("article")).not.toHaveClass("bg-surface-nested");
  });
});
