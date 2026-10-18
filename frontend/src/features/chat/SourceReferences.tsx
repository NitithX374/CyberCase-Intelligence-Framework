"use client";

import { useState } from "react";
import type { SourceMessageRef } from "@/features/citations/types";
import { SourceDrawer } from "@/features/citations/SourceDrawer";
import { SourceCitationChip } from "@/features/citations/SourceCitationChip";
import type { AnalysisSourceReference } from "./chatReferences";

export function SourceReferences({ references }: { references: AnalysisSourceReference[] }) {
  const [active, setActive] = useState<{
    key: string;
    source: SourceMessageRef;
    anchor: HTMLElement;
    role: "supporting" | "conflicting";
  } | null>(null);
  if (references.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap gap-1.5" aria-label="Source references" role="group">
      {references.map((reference, index) => {
        const key = `${reference.role}-${reference.source.id}-${index}`;
        return (
          <SourceCitationChip
            key={key}
            sourceRef={reference.source}
            sourceKey={key}
            isActive={active?.key === key}
            citationRole={reference.role}
            onSelect={(source, anchor, sourceKey) =>
              setActive((current) =>
                current?.key === sourceKey
                  ? null
                  : { key: sourceKey, source, anchor, role: reference.role },
              )
            }
          />
        );
      })}
      {active && (
        <SourceDrawer
          sourceRef={active.source}
          anchorElement={active.anchor}
          onClose={() => setActive(null)}
          citationRole={active.role}
        />
      )}
    </div>
  );
}
