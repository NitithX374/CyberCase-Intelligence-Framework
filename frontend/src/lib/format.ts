type DateStyle = "day" | "dayTime" | "monthDay" | "full";

const DATE_FORMATS: Record<DateStyle, Intl.DateTimeFormatOptions> = {
  day: { month: "short", day: "numeric", year: "numeric" },
  dayTime: { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" },
  monthDay: { month: "short", day: "numeric" },
  full: { dateStyle: "medium", timeStyle: "short" },
};

export function formatDate(value: string | undefined | null, style: DateStyle = "day"): string {
  if (!value) return "Unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unavailable";
  return new Intl.DateTimeFormat("en", DATE_FORMATS[style]).format(date);
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function plural(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}
