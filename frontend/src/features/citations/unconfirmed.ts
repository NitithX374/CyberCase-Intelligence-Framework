import type { SourceMessageRef } from "./types";

export type UnconfirmedStatus = "not_confirmed" | "suspected";

export const NO_CHECKED_QUOTE = "ไม่มี quote ที่ตรวจแล้ว";

export const UNCONFIRMED_NOTES: Record<UnconfirmedStatus, string> = {
  not_confirmed: `ยังไม่ยืนยัน ${NO_CHECKED_QUOTE}`,
  suspected: "อยู่ระหว่างตรวจสอบ",
};

const UNCONFIRMED_ORDER: readonly UnconfirmedStatus[] = ["not_confirmed", "suspected"];

export function isUnconfirmed(status: string | undefined): status is UnconfirmedStatus {
  return status === "not_confirmed" || status === "suspected";
}

export function unconfirmedStatuses(
  statuses: readonly (string | undefined)[],
): UnconfirmedStatus[] {
  return UNCONFIRMED_ORDER.filter((status) => statuses.includes(status));
}

export function checkedSources(
  sources: SourceMessageRef[],
  unconfirmed: boolean,
): SourceMessageRef[] {
  return unconfirmed ? sources.filter((source) => source.exactQuote) : sources;
}
