import { describe, expect, it } from "vitest";
import { AxiosError, AxiosHeaders } from "axios";
import { toUserFacingError } from "@/lib/user-facing-error";

describe("user-facing-error classifier", () => {
  it("maps Axios timeout error to human-facing timeout copy without claiming analysis definitively failed", () => {
    const axiosError = new AxiosError(
      "timeout of 15000ms exceeded",
      "ECONNABORTED",
      undefined,
      undefined,
      undefined,
    );

    const userError = toUserFacingError(axiosError);

    expect(userError.category).toBe("timeout");
    expect(userError.title).toBe("การดำเนินการใช้เวลานานกว่าที่กำหนด");
    expect(userError.message).toBe(
      "ระบบยังไม่สามารถยืนยันผลลัพธ์ได้ในขณะนี้ ข้อมูลที่คุณกรอกไว้ยังคงอยู่ กรุณาลองอีกครั้งหรือตรวจสอบสถานะภายหลัง",
    );
    expect(userError.message).not.toContain("Analysis failed");
    expect(userError.message).not.toContain("ล้มเหลว");
    expect(userError.technicalDetail).toContain("timeout of 15000ms exceeded");
    expect(userError.retryable).toBe(true);
    expect(userError.actionLabel).toBe("ลองอีกครั้ง");
  });

  it("sets actionLabel to 'ตรวจสอบสถานะ' when timeout operation is uncertain", () => {
    const error = new Error("Request timed out");
    const userError = toUserFacingError(error, { isUncertain: true });

    expect(userError.category).toBe("timeout");
    expect(userError.title).toBe("การดำเนินการใช้เวลานานกว่าที่กำหนด");
    expect(userError.actionLabel).toBe("ตรวจสอบสถานะ");
  });

  it("maps raw timeout string to human-facing timeout copy", () => {
    const userError = toUserFacingError("timeout of 15000ms exceeded");

    expect(userError.category).toBe("timeout");
    expect(userError.title).toBe("การดำเนินการใช้เวลานานกว่าที่กำหนด");
    expect(userError.technicalDetail).toBe("timeout of 15000ms exceeded");
  });

  it("maps Network / Connection errors to human-facing network copy", () => {
    const networkError = new AxiosError(
      "Network Error",
      "ERR_NETWORK",
      undefined,
      undefined,
      undefined,
    );

    const userError = toUserFacingError(networkError);

    expect(userError.category).toBe("network");
    expect(userError.title).toBe("ไม่สามารถเชื่อมต่อกับระบบได้");
    expect(userError.message).toBe(
      "ไม่สามารถติดต่อบริการ CyberCase ได้ในขณะนี้ กรุณาตรวจสอบการเชื่อมต่อและลองอีกครั้ง",
    );
    expect(userError.retryable).toBe(true);
  });

  it("maps ECONNRESET and connection strings to network category", () => {
    const userError = toUserFacingError("read ECONNRESET");

    expect(userError.category).toBe("network");
    expect(userError.title).toBe("ไม่สามารถเชื่อมต่อกับระบบได้");
    expect(userError.technicalDetail).toBe("read ECONNRESET");
  });

  it("maps 429 Rate Limit error to human-facing rate limit copy", () => {
    const rateLimitError = new AxiosError(
      "Request failed with status code 429",
      "ERR_BAD_REQUEST",
      undefined,
      undefined,
      {
        status: 429,
        statusText: "Too Many Requests",
        data: "Rate limit exceeded",
        headers: {},
        config: { headers: new AxiosHeaders() },
      },
    );

    const userError = toUserFacingError(rateLimitError);

    expect(userError.category).toBe("rate_limit");
    expect(userError.title).toBe("มีคำขอจำนวนมากในขณะนี้");
    expect(userError.message).toBe(
      "ระบบกำลังรองรับคำขอจำนวนมาก กรุณารอสักครู่แล้วลองอีกครั้ง",
    );
    expect(userError.retryable).toBe(true);
  });

  it("maps 500 Server Error to human-facing server error copy", () => {
    const serverError = new AxiosError(
      "Request failed with status code 500",
      "ERR_BAD_RESPONSE",
      undefined,
      undefined,
      {
        status: 500,
        statusText: "Internal Server Error",
        data: { detail: "Database connection crashed" },
        headers: {},
        config: { headers: new AxiosHeaders() },
      },
    );

    const userError = toUserFacingError(serverError);

    expect(userError.category).toBe("server");
    expect(userError.title).toBe("ระบบไม่สามารถดำเนินการได้");
    expect(userError.message).toBe(
      "เกิดข้อผิดพลาดระหว่างประมวลผลคำขอ กรุณาลองอีกครั้ง",
    );
    expect(userError.technicalDetail).toContain("Database connection crashed");
  });

  it("maps 400 Validation error with safe user message", () => {
    const validationError = new AxiosError(
      "Request failed with status code 400",
      "ERR_BAD_REQUEST",
      undefined,
      undefined,
      {
        status: 400,
        statusText: "Bad Request",
        data: { detail: "กรุณาระบุรายละเอียดเหตุการณ์อย่างน้อย 10 ตัวอักษร" },
        headers: {},
        config: { headers: new AxiosHeaders() },
      },
    );

    const userError = toUserFacingError(validationError);

    expect(userError.category).toBe("validation");
    expect(userError.title).toBe("ข้อมูลไม่ถูกต้องหรือยังไม่สมบูรณ์");
    expect(userError.message).toBe(
      "กรุณาระบุรายละเอียดเหตุการณ์อย่างน้อย 10 ตัวอักษร",
    );
    expect(userError.retryable).toBe(false);
    expect(userError.actionLabel).toBe("ปิด");
  });

  it("maps unknown errors to safe generic copy without leaking technical details into primary message", () => {
    const unknownError = new Error("Unexpected TypeError at Line 42 Object.evaluate");

    const userError = toUserFacingError(unknownError);

    expect(userError.category).toBe("unknown");
    expect(userError.title).toBe("ไม่สามารถดำเนินการได้ในขณะนี้");
    expect(userError.message).toBe(
      "เกิดข้อผิดพลาดที่ไม่คาดคิด กรุณาลองอีกครั้ง",
    );
    expect(userError.message).not.toContain("TypeError");
    expect(userError.technicalDetail).toBe(
      "Unexpected TypeError at Line 42 Object.evaluate",
    );
  });
});
