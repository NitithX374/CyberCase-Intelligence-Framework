import { describe, expect, it } from "vitest";
import { refusal, timeoutError } from "@/test/httpErrors";
import { toUserFacingError } from "./userFacingError";

describe("whether the reader is offered a retry", () => {
  it.each([
    [502, "analysis_provider_down"],
    [503, "analysis_provider_down"],
    [504, "analysis_provider_timeout"],
  ])("offers one when the provider failed with %i", (status, code) => {
    const error = toUserFacingError(refusal(status, code, "The analysis provider failed"));

    expect(error.retryable).toBe(true);
    expect(error.actionLabel).toBe("ลองอีกครั้ง");
    expect(error.technicalDetail).toContain(`Reason: ${code}`);
  });

  it("offers one when the browser stopped waiting", () => {
    expect(toUserFacingError(timeoutError()).retryable).toBe(true);
  });

  it("offers none for a refusal that asking again would not change", () => {
    const error = toUserFacingError(
      refusal(409, "case_sources_changed", "The case sources changed while it ran."),
    );

    expect(error.retryable).toBe(false);
    expect(error.actionLabel).toBe("ปิด");
    expect(error.message).toBe(
      "แหล่งข้อมูลของคดีเปลี่ยนไประหว่างการวิเคราะห์ กรุณาวิเคราะห์อีกครั้ง",
    );
  });
});
