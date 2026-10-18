"use client";

const SCORE_EXPLANATION =
  "How closely the case text matched this technique's ATT&CK description. It does not rate whether the mapping itself is right.";

export function RetrievalScore({
  score,
  retrievedBy,
}: {
  score: number | null;
  retrievedBy: "vector" | "graph";
}) {
  if (retrievedBy === "graph" || score === null) {
    return (
      <span
        className="shrink-0 pt-0.5 text-xs text-ink-muted"
        title="Reached by graph expansion from a matched technique, so it carries no match score."
      >
        via graph
      </span>
    );
  }
  return (
    <span className="shrink-0 pt-0.5 text-xs text-ink-muted" title={SCORE_EXPLANATION}>
      Match {score.toFixed(2)}
    </span>
  );
}
