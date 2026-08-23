import type { MitreCandidateView } from "@/lib/mitre-candidate";

interface MitreCandidatePanelProps {
  candidates: MitreCandidateView[];
}

export function MitreCandidatePanel({
  candidates,
}: MitreCandidatePanelProps) {
  if (candidates.length === 0) return null;

  return (
    <details className="mt-4 overflow-hidden rounded-lg border border-line bg-surface-nested/30">
      <summary className="cursor-pointer list-none px-4 py-3 text-xs font-bold text-ink marker:hidden flex items-center justify-between">
        <span>MITRE candidates · {candidates.length}</span>
        <span className="text-[10px] font-normal text-ink-muted">External technical context</span>
      </summary>
      <div className="space-y-3 border-t border-line p-3">
        {candidates.map((candidate) => (
          <article
            key={candidate.associationId}
            aria-label={`${candidate.techniqueId} MITRE candidate`}
            className="rounded-lg border border-line bg-surface p-4"
          >
            <div className="flex flex-wrap items-baseline gap-2">
              <span className="font-mono text-[10.5px] font-bold text-[#6654A3] bg-[#6654A3]/10 px-1.5 py-0.2 rounded border border-[#6654A3]/20">
                {candidate.techniqueId}
              </span>
              <h4 className="text-sm font-bold text-ink">
                {candidate.techniqueName}
              </h4>
            </div>

            <div className="mt-3">
              <p className="text-[10px] font-bold uppercase tracking-wide text-ink-secondary">
                Linked analysis
              </p>
              <ul className="mt-1.5 space-y-1.5">
                {candidate.claims.map((claim) => (
                  <li key={claim.claimId} className="text-xs leading-relaxed text-ink-secondary">
                    <span className="mr-2 rounded border border-line bg-surface px-1.5 py-0.5 font-mono text-[10px] font-bold text-ink">
                      {claim.claimId}
                    </span>
                    {claim.text}
                  </li>
                ))}
              </ul>
            </div>

            <div className="mt-3 border-t border-line pt-3">
              <p className="text-[10px] font-bold uppercase tracking-wide text-ink-secondary">
                Why this candidate?
              </p>
              <p className="mt-1 text-xs leading-relaxed text-ink-secondary">
                {candidate.reason}
              </p>
            </div>

            <div className="mt-3 flex flex-wrap gap-1.5 text-[10px] font-medium text-ink-muted">
              <span className="rounded border border-line bg-surface-nested/50 px-2 py-0.5">Candidate only</span>
              <span className="rounded border border-line bg-surface-nested/50 px-2 py-0.5">External technical context</span>
              <span className="rounded border border-line bg-surface-nested/50 px-2 py-0.5">Not incident evidence</span>
            </div>
          </article>
        ))}
      </div>
    </details>
  );
}
