import { describe, expect, it } from "vitest";
import { quotedPassage, readable } from "@/features/citations/quotedPassage";

describe("readable", () => {
  it("shows OCR table and page-number markup as plain text", () => {
    expect(
      readable("<tr><td>3 มีนาคม 2569</td><td>123-4-56789</td></tr><page_number>2</page_number>"),
    ).toBe("3 มีนาคม 2569 | 123-4-56789\n");
  });

  it("keeps markup that is not the OCR's own, such as a link in a phishing email", () => {
    expect(readable('Click <a href="https://login.bank-example.test">here</a>')).toBe(
      'Click <a href="https://login.bank-example.test">here</a>',
    );
  });
});

describe("quotedPassage", () => {
  it("places the quote between the text around it", () => {
    expect(
      quotedPassage("a transfer of 52,000 baht", {
        before: "The caller said the account had been frozen. He asked for ",
        after: " to a safe account.",
        cutBefore: false,
        cutAfter: false,
      }),
    ).toEqual({
      before: "The caller said the account had been frozen. He asked for ",
      quote: "a transfer of 52,000 baht",
      after: " to a safe account.",
    });
  });

  it("marks a side that was trimmed", () => {
    const passage = quotedPassage("123-4-56789", {
      before: "<td>3 มีนาคม 2569</td><td>",
      after: "</td><td>52,000 บาท</td>",
      cutBefore: true,
      cutAfter: true,
    });

    expect(`${passage.before}[${passage.quote}]${passage.after}`).toBe(
      "… 3 มีนาคม 2569 | [123-4-56789] | 52,000 บาท …",
    );
  });

  it("shows the quote alone when it is its whole sentence or has no context", () => {
    const whole = { before: "", after: "", cutBefore: false, cutAfter: false };

    expect(quotedPassage("The money was gone.", whole)).toEqual({
      before: "",
      quote: "The money was gone.",
      after: "",
    });
    expect(quotedPassage("The money was gone.", null)).toEqual({
      before: "",
      quote: "The money was gone.",
      after: "",
    });
  });
});
