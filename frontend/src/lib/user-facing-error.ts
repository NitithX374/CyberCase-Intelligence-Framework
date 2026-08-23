import axios from "axios";

export type ErrorCategory =
  | "timeout"
  | "network"
  | "rate_limit"
  | "server"
  | "validation"
  | "unknown";

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
    message:
      "ไม่สามารถติดต่อบริการ CyberCase ได้ในขณะนี้ กรุณาตรวจสอบการเชื่อมต่อและลองอีกครั้ง",
  },
  rate_limit: {
    title: "มีคำขอจำนวนมากในขณะนี้",
    message: "ระบบกำลังรองรับคำขอจำนวนมาก กรุณารอสักครู่แล้วลองอีกครั้ง",
  },
  server: {
    title: "ระบบไม่สามารถดำเนินการได้",
    message: "เกิดข้อผิดพลาดระหว่างประมวลผลคำขอ กรุณาลองอีกครั้ง",
  },
  validation: {
    title: "ข้อมูลไม่ถูกต้องหรือยังไม่สมบูรณ์",
    message: "กรุณาตรวจสอบข้อมูลที่ระบุแล้วลองอีกครั้ง",
  },
  unknown: {
    title: "ไม่สามารถดำเนินการได้ในขณะนี้",
    message: "เกิดข้อผิดพลาดที่ไม่คาดคิด กรุณาลองอีกครั้ง",
  },
} as const;

function isTimeoutString(str: string): boolean {
  return /timeout|timed?\s*out|15000ms|gateway\s*timeout|504/i.test(str);
}

function isNetworkString(str: string): boolean {
  return (
    /network\s*error|failed\s*to\s*fetch|econnrefused|econnreset|err_network|net::err|connection\s*refused|connection\s*reset/i.test(
      str,
    )
  );
}

function isRateLimitString(str: string): boolean {
  return /429|too\s*many\s*requests|rate\s*limit/i.test(str);
}

function isServerErrorString(str: string): boolean {
  return /500|502|503|internal\s*server\s*error|server\s*error|backend\s*error/i.test(
    str,
  );
}

export function toUserFacingError(
  rawError: unknown,
  options?: {
    isUncertain?: boolean;
    actionLabel?: string;
  },
): UserFacingError {
  if (!rawError) {
    return {
      title: ERROR_COPY.unknown.title,
      message: ERROR_COPY.unknown.message,
      retryable: true,
      category: "unknown",
      actionLabel: options?.actionLabel ?? "ลองอีกครั้ง",
    };
  }

  let technicalDetail: string | undefined;
  let category: ErrorCategory = "unknown";
  let customUserMessage: string | undefined;

  if (axios.isAxiosError(rawError)) {
    const status = rawError.response?.status;
    const code = rawError.code;
    const rawMsg = rawError.message || "";
    const responseData = rawError.response?.data;

    let responseDetailStr = "";
    if (typeof responseData === "string" && responseData.trim()) {
      responseDetailStr = responseData.trim();
    } else if (
      responseData &&
      typeof responseData === "object" &&
      "detail" in responseData
    ) {
      const detail = (responseData as { detail?: unknown }).detail;
      if (typeof detail === "string") responseDetailStr = detail.trim();
      else if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0];
        if (typeof first === "string") responseDetailStr = first.trim();
        else if (first && typeof first === "object" && "msg" in first) {
          responseDetailStr = String((first as { msg: unknown }).msg).trim();
        }
      }
    }

    technicalDetail = [
      rawMsg ? `Message: ${rawMsg}` : null,
      code ? `Code: ${code}` : null,
      status ? `Status: ${status}` : null,
      responseDetailStr ? `Detail: ${responseDetailStr}` : null,
    ]
      .filter(Boolean)
      .join(" | ");

    if (
      code === "ECONNABORTED" ||
      code === "ETIMEDOUT" ||
      status === 408 ||
      status === 504 ||
      isTimeoutString(rawMsg)
    ) {
      category = "timeout";
    } else if (status === 429 || isRateLimitString(rawMsg)) {
      category = "rate_limit";
    } else if (
      code === "ERR_NETWORK" ||
      !rawError.response ||
      isNetworkString(rawMsg)
    ) {
      category = "network";
    } else if (status && status >= 500) {
      category = "server";
    } else if (status && status >= 400 && status < 500) {
      category = "validation";
      if (responseDetailStr && !isNetworkString(responseDetailStr) && !isServerErrorString(responseDetailStr)) {
        customUserMessage = responseDetailStr;
      }
    } else {
      category = "unknown";
    }
  } else if (rawError instanceof Error) {
    const msg = rawError.message.trim();
    technicalDetail = msg;

    if (isTimeoutString(msg)) {
      category = "timeout";
    } else if (isNetworkString(msg)) {
      category = "network";
    } else if (isRateLimitString(msg)) {
      category = "rate_limit";
    } else if (isServerErrorString(msg)) {
      category = "server";
    } else {
      category = "unknown";
    }
  } else if (typeof rawError === "string") {
    const trimmed = rawError.trim();
    technicalDetail = trimmed;

    if (isTimeoutString(trimmed)) {
      category = "timeout";
    } else if (isNetworkString(trimmed)) {
      category = "network";
    } else if (isRateLimitString(trimmed)) {
      category = "rate_limit";
    } else if (isServerErrorString(trimmed)) {
      category = "server";
    } else {
      category = "unknown";
    }
  }

  const baseCopy = ERROR_COPY[category];
  const retryable = category !== "validation";

  let defaultActionLabel = "ลองอีกครั้ง";
  if (category === "timeout" && options?.isUncertain) {
    defaultActionLabel = "ตรวจสอบสถานะ";
  } else if (!retryable) {
    defaultActionLabel = "ปิด";
  }

  return {
    title: baseCopy.title,
    message: customUserMessage || baseCopy.message,
    technicalDetail: technicalDetail || undefined,
    retryable,
    category,
    actionLabel: options?.actionLabel ?? defaultActionLabel,
  };
}
