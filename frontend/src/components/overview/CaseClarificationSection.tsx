"use client";

import { useState, type FormEvent } from "react";
import type { CaseClarificationRead } from "@/lib/api";

interface CaseClarificationSectionProps {
  clarifications: CaseClarificationRead[];
  submittingId: string | null;
  onAnswer: (clarificationId: string, answer: string) => void;
}

export function CaseClarificationSection({
  clarifications,
  submittingId,
  onAnswer,
}: CaseClarificationSectionProps) {
  const pending = clarifications.filter((item) => item.state === "pending");
  if (pending.length === 0) return null;
  return (
    <section aria-labelledby="case-clarification-heading" className="order-4 min-w-0 border-t border-line pt-4 lg:order-2">
      <h2 id="case-clarification-heading" className="text-sm font-semibold text-ink">Clarification needed</h2>
      <div className="divide-y divide-line">
        {pending.map((clarification) => (
          <ClarificationForm
            key={clarification.id}
            clarification={clarification}
            isSubmitting={submittingId === clarification.id}
            onAnswer={onAnswer}
          />
        ))}
      </div>
    </section>
  );
}

function ClarificationForm({
  clarification,
  isSubmitting,
  onAnswer,
}: {
  clarification: CaseClarificationRead;
  isSubmitting: boolean;
  onAnswer: (clarificationId: string, answer: string) => void;
}) {
  const [answer, setAnswer] = useState("");
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!answer.trim() || isSubmitting) return;
    onAnswer(clarification.id, answer.trim());
  };
  return (
    <form onSubmit={handleSubmit} className="space-y-3 py-4 last:pb-1">
      <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-muted">{clarification.topic}</p>
      <p className="text-sm leading-6 text-ink">{clarification.question}</p>
      <label className="block space-y-1.5">
        <span className="text-xs font-semibold text-ink">Your answer</span>
        <textarea
          aria-label={`Answer: ${clarification.topic}`}
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          disabled={isSubmitting}
          rows={4}
          className="block w-full resize-y rounded-lg border border-line bg-canvas p-3 text-sm leading-6 text-ink outline-none focus:border-ink disabled:bg-surface-nested"
        />
      </label>
      <button type="submit" disabled={!answer.trim() || isSubmitting} className="btn-primary min-h-9 rounded-lg text-xs disabled:cursor-not-allowed">
        {isSubmitting ? "Submitting answer…" : "Submit answer and re-analyze"}
      </button>
    </form>
  );
}
