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
    <header className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-3">
      <div className="min-w-0">
        {eyebrow && <p className="section-eyebrow">{eyebrow}</p>}
        <h2
          id={headingId}
          className="mt-1 text-lg font-extrabold tracking-[-0.025em] text-ink sm:text-xl"
        >
          {title}
        </h2>
        {description && (
          <p className="mt-1 max-w-2xl text-xs leading-relaxed text-ink-secondary">
            {description}
          </p>
        )}
      </div>
      {aside && <div className="shrink-0">{aside}</div>}
    </header>
  );
}
