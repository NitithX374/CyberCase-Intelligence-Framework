import type { ReactNode } from "react";
import { Icon } from "./icons";

export function EmptyState({
  title,
  description,
  titleAs: Title = "h2",
  busy = false,
  className = "",
  children,
}: {
  title: string;
  description?: string;
  titleAs?: "h2" | "h3";
  busy?: boolean;
  className?: string;
  children?: ReactNode;
}) {
  return (
    <div className={`flex flex-col items-center text-center ${className}`}>
      {busy && <Icon name="spinner" className="mb-4 h-5 w-5 text-ink-muted" />}
      <Title className="text-lg font-semibold tracking-tight text-ink">{title}</Title>
      {description && (
        <p className="mt-1 max-w-sm text-sm leading-6 text-ink-muted">{description}</p>
      )}
      {children}
    </div>
  );
}
