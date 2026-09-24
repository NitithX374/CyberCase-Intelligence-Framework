import axios, { type AxiosError } from "axios";
import { asRecord, asString } from "@/lib/parse";

export type ErrorCategory = "timeout" | "network" | "rate_limit" | "server" | "refused" | "unknown";

export interface UserFacingError {
  title: string;
  message: string;
  technicalDetail?: string;
  retryable: boolean;
  category: ErrorCategory;
  actionLabel?: string;
}

const ERROR_COPY = {
  timeout: {
    title: "การดำเนินการใช้เวลานานกว่าที่กำหนด",
    message:
      "ระบบยังไม่สามารถยืนยันผลลัพธ์ได้ในขณะนี้ ข้อมูลที่คุณกรอกไว้ยังคงอยู่ กรุณาลองอีกครั้งหรือตรวจสอบสถานะภายหลัง",
  },
  network: {
    title: "ไม่สามารถเชื่อมต่อกับระบบได้",
    message: "ไม่สามารถติดต่อบริการ CyberCase ได้ในขณะนี้ กรุณาตรวจสอบการเชื่อมต่อและลองอีกครั้ง",
  },
  rate_limit: {
    title: "มีคำขอจำนวนมากในขณะนี้",
    message: "ระบบกำลังรองรับคำขอจำนวนมาก กรุณารอสักครู่แล้วลองอีกครั้ง",
  },
  server: {
    title: "ระบบไม่สามารถดำเนินการได้",
    message: "เกิดข้อผิดพลาดระหว่างประมวลผลคำขอ กรุณาลองอีกครั้ง",
  },
  refused: {
    title: "ระบบไม่ดำเนินการตามคำขอนี้",
    message: "กรุณาตรวจสอบข้อมูลที่ระบุแล้วลองอีกครั้ง",
  },
  unknown: {
    title: "ไม่สามารถดำเนินการได้ในขณะนี้",
    message: "เกิดข้อผิดพลาดที่ไม่คาดคิด กรุณาลองอีกครั้ง",
  },
} as const;

export function detailMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail = responseDetail(error.response?.data);
    if (detail) return detail;
  }
  if (error instanceof Error && error.message.trim()) return error.message.trim();
  return fallback;
}

export function toUserFacingError(
  error: unknown,
  options?: { actionLabel?: string },
): UserFacingError {
  const category = axios.isAxiosError(error) ? categoryOf(error) : "unknown";
  const detail = axios.isAxiosError(error) ? responseDetail(error.response?.data) : "";
  const retryable = category !== "refused";
  return {
    title: ERROR_COPY[category].title,
    message: (category === "refused" && detail) || ERROR_COPY[category].message,
    technicalDetail: technicalDetail(error, detail) || undefined,
    retryable,
    category,
    actionLabel: options?.actionLabel ?? (retryable ? "ลองอีกครั้ง" : "ปิด"),
  };
}

function categoryOf(error: AxiosError): ErrorCategory {
  const status = error.response?.status;
  if (
    error.code === "ECONNABORTED" ||
    error.code === "ETIMEDOUT" ||
    status === 408 ||
    status === 504
  ) {
    return "timeout";
  }
  if (status === 429) return "rate_limit";
  if (status === undefined) return "network";
  if (status >= 500) return "server";
  if (status >= 400) return "refused";
  return "unknown";
}

function responseDetail(data: unknown): string {
  if (typeof data === "string") return data.trim();
  const detail = asRecord(data)?.detail;
  const first = Array.isArray(detail) ? detail[0] : detail;
  if (typeof first === "string") return first.trim();
  const record = asRecord(first);
  return asString(record?.message) || asString(record?.msg);
}

function technicalDetail(error: unknown, detail: string): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error ? error.message.trim() : "";
  }
  const code = asString(asRecord(asRecord(error.response?.data)?.detail)?.code);
  return [
    error.message ? `Message: ${error.message}` : null,
    error.code ? `Code: ${error.code}` : null,
    error.response?.status ? `Status: ${error.response.status}` : null,
    code ? `Reason: ${code}` : null,
    detail ? `Detail: ${detail}` : null,
  ]
    .filter(Boolean)
    .join(" | ");
}
