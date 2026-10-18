"use client";

import type { RetrievedTechnicalContextCard } from "./technicalContext";
import { TechniqueTitle } from "./TechniqueTitle";

export function RetrievedOnlyItem({ item }: { item: RetrievedTechnicalContextCard }) {
  return (
    <li className="py-3">
      <TechniqueTitle
        techniqueId={item.techniqueId}
        techniqueName={item.techniqueName}
        tactic={item.tactic}
        mitreUrl={item.mitreUrl}
        as="h4"
      />
      {item.fullTechnicalDefinition && (
        <p className="mt-1 line-clamp-2 text-sm leading-6 text-ink-secondary select-text">
          {item.fullTechnicalDefinition}
        </p>
      )}
    </li>
  );
}
