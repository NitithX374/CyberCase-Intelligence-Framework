"use client";

import { SUGGESTION_LINES } from "./ChatTranscript";

export function SuggestionLine({ suggestion }: { suggestion?: string }) {
  const line = suggestion ? SUGGESTION_LINES[suggestion] : undefined;
  if (!line) return null;
  return <p className="mt-3 text-[13px] text-ink-muted">{line}</p>;
}
