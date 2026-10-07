import { hasThai } from "@/lib/language";
import { citedSourcePassages } from "./groupSourceRefs";
import { quotedPassage } from "./quotedPassage";
import type { SourceMessageRef } from "./types";

const POINTER_LABELS = {
  direct: "Linked directly",
  recovered: "Recovered location",
  legacy: "Legacy citation",
  unresolved: "Unresolved reference",
};

const THAI_POINTER_LABELS = {
  direct: "เชื่อม Source โดยตรง",
  recovered: "ค้นคืนตำแหน่งใน Source",
  legacy: "การอ้างอิงแบบเดิม",
  unresolved: "เชื่อมตำแหน่งใน Source ไม่ได้",
};

export function SourcePassages({ sourceRef }: { sourceRef: SourceMessageRef }) {
  const passages = citedSourcePassages(sourceRef);
  if (passages.length === 0) return null;
  return (
    <section aria-label="Cited Source passages" className="mb-6 space-y-3">
      {passages.map((cited, index) => {
        const passage = quotedPassage(cited.quote, cited.context);
        const thai = hasThai(cited.quote);
        const label =
          passages.length > 1
            ? thai
              ? `ข้อความ Source ${index + 1} จาก ${passages.length}`
              : `Source passage ${index + 1} of ${passages.length}`
            : (sourceRef.quoteLabel ?? "Quoted");
        return (
          <section key={index} className="rounded-xl border border-line bg-surface-nested p-4">
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-muted">
              {label}
            </h3>
            <p className="select-text text-[15px] leading-7 text-ink [overflow-wrap:anywhere]">
              {passage.before}
              {passage.before || passage.after ? (
                <strong className="font-semibold bg-amber-200/60 dark:bg-amber-400/30 text-ink px-1 py-0.5 rounded">
                  {passage.quote}
                </strong>
              ) : (
                <mark className="bg-amber-200/60 dark:bg-amber-400/30 text-ink px-1 py-0.5 rounded font-semibold not-italic">
                  {passage.quote}
                </mark>
              )}
              {passage.after}
            </p>
            <p className="mt-2 text-xs text-ink-muted">
              {(thai ? THAI_POINTER_LABELS : POINTER_LABELS)[cited.pointerState]}
            </p>
            {cited.notes.map((note, noteIndex) => (
              <p key={noteIndex} className="mt-2 text-xs text-ink-muted [overflow-wrap:anywhere]">
                {note}
              </p>
            ))}
          </section>
        );
      })}
    </section>
  );
}
