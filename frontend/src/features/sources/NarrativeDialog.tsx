"use client";

import { useState, type FormEvent } from "react";
import { Icon } from "@/components/icons";
import { Dialog } from "@/components/Dialog";
import type { NarrativeSubmission } from "./CaseSourcesView";

export function NarrativeDialog({
  isOpen,
  isSaving,
  onCancel,
  onSubmit,
}: {
  isOpen: boolean;
  isSaving: boolean;
  onCancel: () => void;
  onSubmit: (submission: NarrativeSubmission) => void;
}) {
  return (
    <Dialog
      isOpen={isOpen}
      onDismiss={onCancel}
      canDismiss={!isSaving}
      labelledBy="case-narrative-title"
      className="w-[min(38rem,calc(100vw-2rem))]"
    >
      {isOpen && <NarrativeForm isSaving={isSaving} onCancel={onCancel} onSubmit={onSubmit} />}
    </Dialog>
  );
}

function NarrativeForm({
  isSaving,
  onCancel,
  onSubmit,
}: {
  isSaving: boolean;
  onCancel: () => void;
  onSubmit: (submission: NarrativeSubmission) => void;
}) {
  const [text, setText] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!text.trim() || isSaving) return;
    onSubmit({ text: text.trim() });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2 id="case-narrative-title" className="text-lg font-semibold tracking-tight">
        Case narrative
      </h2>

      <label htmlFor="case-narrative-text" className="mt-5 block text-[13px] font-medium text-ink">
        Narrative
      </label>
      <textarea
        id="case-narrative-text"
        data-autofocus
        rows={8}
        value={text}
        onChange={(event) => setText(event.target.value)}
        disabled={isSaving}
        placeholder="What happened, who was involved, and when."
        className="mt-1.5 block min-h-44 w-full resize-y rounded-lg border border-line-strong bg-surface p-3 text-[15px] leading-7 text-ink outline-none placeholder:text-ink-muted focus:border-ink disabled:bg-surface-nested"
      />

      <div className="mt-6 flex justify-end gap-2">
        <button type="button" disabled={isSaving} onClick={onCancel} className="btn-ghost">
          Cancel
        </button>
        <button type="submit" disabled={isSaving || !text.trim()} className="btn-primary">
          {isSaving && <Icon name="spinner" className="h-4 w-4" />}
          {isSaving ? "Saving…" : "Add narrative"}
        </button>
      </div>
    </form>
  );
}
