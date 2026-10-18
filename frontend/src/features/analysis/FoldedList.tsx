"use client";

import { useState, type ReactNode } from "react";

const VISIBLE_ROWS = 6;

export function FoldedList<T>({
  items,
  label,
  as: List = "ul",
  className,
  render,
}: {
  items: T[];
  label: string;
  as?: "ul" | "ol";
  className: string;
  render: (item: T, index: number) => ReactNode;
}) {
  const [expanded, setExpanded] = useState(false);
  const folds = items.length > VISIBLE_ROWS;
  const shown = expanded || !folds ? items : items.slice(0, VISIBLE_ROWS);

  return (
    <>
      <List className={className}>{shown.map(render)}</List>
      {folds && (
        <button
          type="button"
          onClick={() => setExpanded((open) => !open)}
          className="mt-3 text-[13px] font-medium text-ink-secondary hover:text-ink"
        >
          {expanded ? "Show fewer" : `Show all ${items.length}`}{" "}
          <span className="sr-only">{label}</span>
        </button>
      )}
    </>
  );
}
