import type { ReactNode } from "react";

interface WorkspaceSectionHeaderProps {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  headingId?: string;
  aside?: ReactNode;
}

export function WorkspaceSectionHeader({
  eyebrow,
  title,
  description,
  headingId,
  aside,
}: WorkspaceSectionHeaderProps) {
  return (
    <header className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-2.5">
      <div className="min-w-0">
        {eyebrow && <p className="section-eyebrow">{eyebrow}</p>}
        <h2
          id={headingId}
          className={`${eyebrow ? "mt-1" : ""} text-sm font-semibold tracking-[-0.01em] text-ink`}
        >
          {title}
        </h2>
        {description && (
          <p className="mt-1 max-w-2xl text-[11px] leading-5 text-ink-secondary">
            {description}
          </p>
        )}
      </div>
      {aside && <div className="shrink-0">{aside}</div>}
    </header>
  );
}
