"use client";

import { UNCONFIRMED_NOTES } from "@/features/citations/unconfirmed";
import type { ReferenceList } from "./chatReferences";
import { SourceReferences } from "./SourceReferences";

export function AnswerReferences({ references, unconfirmed }: ReferenceList) {
  return (
    <>
      {unconfirmed.map((status) => (
        <p key={status} className="mt-1 text-xs text-ink-muted">
          {UNCONFIRMED_NOTES[status]}
        </p>
      ))}
      <SourceReferences references={references} />
    </>
  );
}
