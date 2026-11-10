import type { ReactNode } from "react";
import { Icon } from "./icons";

export function EmptyState({
  title,
  description,
  titleAs: Title = "h2",
  busy = false,
  illustrated = true,
  className = "",
  children,
}: {
  title: string;
  description?: string;
  titleAs?: "h2" | "h3";
  busy?: boolean;
  illustrated?: boolean;
  className?: string;
  children?: ReactNode;
}) {
  return (
    <div className={`flex flex-col items-center text-center ${className}`}>
      {busy ? (
        <Icon name="spinner" className="mb-4 h-5 w-5 text-ink-muted" />
      ) : (
        illustrated && <CaseFileDrawing />
      )}
      <Title className="text-lg font-semibold tracking-tight text-ink">{title}</Title>
      {description && (
        <p className="mt-1 max-w-sm text-sm leading-6 text-ink-muted">{description}</p>
      )}
      {children}
    </div>
  );
}

function CaseFileDrawing() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 64 64"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="draw-line mb-4 h-14 w-14 text-primary"
    >
      <path
        pathLength="1"
        d="M8 18v34a4 4 0 0 0 4 4h40a4 4 0 0 0 4-4V24a4 4 0 0 0-4-4H30l-5-6H12a4 4 0 0 0-4 4Z"
      />
      <path pathLength="1" d="M20 34h24" />
      <path pathLength="1" d="M20 42h16" />
    </svg>
  );
}
