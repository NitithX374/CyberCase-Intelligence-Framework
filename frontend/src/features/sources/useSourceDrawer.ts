"use client";

import { useCallback, useState } from "react";
import type { SourceMessageRef } from "./types";

export interface OpenSource {
  sourceRef: SourceMessageRef;
  anchorElement: HTMLElement;
  /** The citation that opened it, so the same citation closes it again. */
  key: string;
  citationRole?: "supporting" | "conflicting";
}

/** The source drawer a page opens from its citations, one source at a time. */
export function useSourceDrawer() {
  const [open, setOpen] = useState<OpenSource | null>(null);
  const toggle = useCallback(
    (next: OpenSource) => setOpen((current) => (current?.key === next.key ? null : next)),
    [],
  );
  const close = useCallback(() => setOpen(null), []);
  return { open, openKey: open?.key ?? null, toggle, close };
}
