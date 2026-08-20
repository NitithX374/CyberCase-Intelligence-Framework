import type { MitreCandidateView } from "@/lib/mitre-candidate";

interface MitreCandidatePanelProps {
  candidates: MitreCandidateView[];
}

export function MitreCandidatePanel({
  candidates,
}: MitreCandidatePanelProps) {
  if (candidates.length === 0) return null;

  return (
    <details className="mt-4 overflow-hidden rounded-xl border border-[#d8d3e3] bg-[#f7f5f9]">
      <summary className="cursor-pointer list-none px-4 py-3 text-xs font-bold text-[#51495d] marker:hidden">
        MITRE candidates · {candidates.length}
      </summary>
      <div className="space-y-3 border-t border-[#ddd8e5] p-3">
        {candidates.map((candidate) => (
          <article
            key={candidate.associationId}
            aria-label={`${candidate.techniqueId} MITRE candidate`}
            className="rounded-lg border border-[#ddd8e5] bg-white p-4"
          >
            <p className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-[#756b82]">
              MITRE candidate
            </p>
            <h4 className="mt-1 text-sm font-extrabold text-ink">
              {candidate.techniqueId} — {candidate.techniqueName}
            </h4>

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

            <div className="mt-3 flex flex-wrap gap-1.5 text-[10px] font-semibold text-[#665b73]">
              <span className="rounded-full border border-[#d8d3e3] px-2 py-1">Candidate only</span>
              <span className="rounded-full border border-[#d8d3e3] px-2 py-1">External technical context</span>
              <span className="rounded-full border border-[#d8d3e3] px-2 py-1">Not incident evidence</span>
            </div>
          </article>
        ))}
      </div>
    </details>
  );
}
