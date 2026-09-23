import type { ReactNode } from "react";
import { Icon, type IconName } from "@/components/common/icons";

/** A centred placeholder: an icon, a line saying why the space is empty, and what to do. */
export function EmptyState({
  icon,
  title,
  description,
  titleAs: Title = "h2",
  className = "",
  children,
}: {
  icon: IconName;
  title: string;
  description?: string;
  titleAs?: "h2" | "h3";
  className?: string;
  children?: ReactNode;
}) {
  return (
    <div className={`flex flex-col items-center text-center ${className}`}>
      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-surface-nested text-ink-muted">
        <Icon name={icon} className="h-5 w-5" />
      </span>
      <Title className="mt-4 text-lg font-semibold tracking-tight text-ink">{title}</Title>
      {description && (
        <p className="mt-1 max-w-sm text-sm leading-6 text-ink-muted">{description}</p>
      )}
      {children}
    </div>
  );
}
