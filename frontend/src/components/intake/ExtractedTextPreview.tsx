"use client";

import { useEffect, useId, useRef, useState } from "react";
import { intakeReadableText } from "@/lib/intake-readable-text";

const modes = ["Overview", "Extracted Text", "Raw Text"] as const;
type ContentMode = typeof modes[number];

export function ExtractedTextPreview({ text, label, onEdit }: {
  text: string;
  label: string;
  onEdit?: (text: string) => void;
}) {
  const [mode, setMode] = useState<ContentMode>("Overview");
  const [expanded, setExpanded] = useState(false);
  const id = useId();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const openerRef = useRef<HTMLButtonElement>(null);
  const readable = intakeReadableText(text);
  const displayed = mode === "Raw Text" ? text : readable;

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (expanded && !dialog.open) dialog.showModal();
    if (!expanded && dialog.open) {
      dialog.close();
      openerRef.current?.focus();
    }
  }, [expanded]);

  return (
    <section aria-label={label} className="min-w-0">
      <div role="tablist" aria-label={`${label} views`} className="flex gap-4 border-b border-line">
        {modes.map((item, index) => (
          <button
            key={item} type="button" role="tab" id={`${id}-tab-${index}`}
            aria-selected={mode === item} aria-controls={`${id}-content`}
            tabIndex={mode === item ? 0 : -1}
            onClick={() => setMode(item)}
            onKeyDown={(event) => {
              const next = event.key === "ArrowRight" ? (index + 1) % modes.length
                : event.key === "ArrowLeft" ? (index + modes.length - 1) % modes.length
                  : event.key === "Home" ? 0 : event.key === "End" ? modes.length - 1 : null;
              if (next === null) return;
              event.preventDefault();
              setMode(modes[next]);
              document.getElementById(`${id}-tab-${next}`)?.focus();
            }}
            className={`min-h-10 border-b-2 text-xs outline-none focus-visible:ring-2 focus-visible:ring-primary ${mode === item ? "border-ink font-semibold text-ink" : "border-transparent text-ink-muted hover:text-ink"}`}
          >{item}</button>
        ))}
      </div>
      <div role="tabpanel" id={`${id}-content`} aria-labelledby={`${id}-tab-${modes.indexOf(mode)}`} tabIndex={0} className="pt-4 outline-none focus-visible:ring-1 focus-visible:ring-primary">
        <p className="mb-3 text-[11px] text-ink-muted">
          {mode === "Raw Text" ? "Original source text. Markup is shown as text only."
            : "Reading copy with document markup removed. Original text is retained for analysis and citations."}
        </p>
        {mode === "Raw Text" && onEdit ? (
          <textarea aria-label="Edit raw narrative" value={text} onChange={(event) => onEdit(event.target.value)} rows={10} className="block max-h-80 min-h-48 w-full resize-y rounded border border-line bg-canvas p-3 font-mono text-xs leading-6 outline-none focus:border-ink" />
        ) : (
          <div className="max-h-80 overflow-y-auto rounded border border-line bg-canvas/40 p-4" tabIndex={0} aria-label={`${label} text`}>
            <p className={`whitespace-pre-wrap break-words text-sm leading-7 text-ink ${mode === "Overview" ? "line-clamp-[12]" : ""} ${mode === "Raw Text" ? "font-mono text-xs" : ""}`}>
              {displayed || "No readable text was produced."}
            </p>
          </div>
        )}
        <button ref={openerRef} type="button" onClick={() => setExpanded(true)} className="mt-3 min-h-9 text-xs font-semibold underline decoration-line-strong underline-offset-4 hover:decoration-ink focus-visible:outline-2">
          {mode === "Raw Text" ? "View full raw text" : "View full extracted text"} →
        </button>
      </div>
      <dialog ref={dialogRef} aria-labelledby={`${id}-reader-title`} onCancel={(event) => { event.preventDefault(); setExpanded(false); }} className="m-auto max-h-[90dvh] w-[calc(100%-2rem)] max-w-4xl overflow-hidden rounded-xl border border-line bg-surface p-0 text-ink backdrop:bg-ink/40">
        <div className="flex items-start justify-between gap-4 border-b border-line px-5 py-4">
          <h2 id={`${id}-reader-title`} className="min-w-0 break-words text-sm font-bold">{label} · {mode === "Raw Text" ? "Raw text" : "Extracted text"}</h2>
          <button type="button" onClick={() => setExpanded(false)} className="shrink-0 text-xs font-semibold underline underline-offset-4">Close</button>
        </div>
        <div className="max-h-[70dvh] overflow-y-auto p-5 sm:p-8" tabIndex={0}>
          <p className="whitespace-pre-wrap break-words text-sm leading-7">{displayed}</p>
        </div>
      </dialog>
    </section>
  );
}
