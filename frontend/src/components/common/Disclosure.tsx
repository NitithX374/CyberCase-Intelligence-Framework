import type { ReactNode } from "react";
import { Icon } from "@/components/common/icons";

/** The small "Reasoning ⌄" toggle that opens a detail below a row. */
export function DisclosureToggle({
  label,
  isOpen,
  onToggle,
  controls,
  className = "",
}: {
  label: string;
  isOpen: boolean;
  onToggle: () => void;
  controls: string;
  className?: string;
}) {
  return (
    <button
      type="button"
      aria-expanded={isOpen}
      aria-controls={controls}
      onClick={onToggle}
      className={`inline-flex h-6 items-center gap-0.5 rounded-md px-1.5 text-xs font-medium text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink ${className}`}
    >
      {label}
      <Icon
        name="chevron"
        className={`h-3.5 w-3.5 transition-transform duration-150 ${isOpen ? "rotate-180" : ""}`}
      />
    </button>
  );
}

/** What a disclosure opens: a quiet, indented block under its row. */
export function DisclosurePanel({
  id,
  children,
  className = "",
}: {
  id: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      id={id}
      className={`border-l-2 border-line-strong pl-3 text-sm leading-6 text-ink-secondary ${className}`}
    >
      {children}
    </div>
  );
}
