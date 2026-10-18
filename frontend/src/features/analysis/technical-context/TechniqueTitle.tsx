"use client";

import { Icon } from "@/components/icons";

export function TechniqueTitle({
  techniqueId,
  techniqueName,
  tactic,
  mitreUrl,
  as: Heading = "h3",
}: {
  techniqueId: string;
  techniqueName: string;
  tactic: string;
  mitreUrl: string;
  as?: "h3" | "h4";
}) {
  return (
    <div className="flex min-w-0 flex-wrap items-baseline gap-x-2 gap-y-0.5">
      <a
        href={mitreUrl}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`Open ${techniqueId} on MITRE ATT&CK`}
        title={`Open ${techniqueId} on MITRE ATT&CK`}
        className="group inline-flex items-center gap-1 font-mono text-[13px] font-medium text-ink-secondary transition-colors hover:text-ink hover:underline"
      >
        <span>{techniqueId}</span>
        <Icon
          name="external"
          className="h-3 w-3 text-ink-muted transition-colors group-hover:text-ink"
        />
      </a>
      <Heading className="text-[15px] font-semibold text-ink">
        <a
          href={mitreUrl}
          target="_blank"
          rel="noopener noreferrer"
          title={`Open ${techniqueName} on MITRE ATT&CK`}
          className="transition-colors hover:text-ink-secondary hover:underline"
        >
          {techniqueName}
        </a>
      </Heading>
      {tactic && <span className="text-[13px] text-ink-muted">{tactic}</span>}
    </div>
  );
}
