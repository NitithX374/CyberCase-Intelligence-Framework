import { Icon } from "@/components/common/icons";
import type { MitreCandidateView } from "@/lib/mitre-candidate";

interface CaseStateMitreViewProps {
  candidates: MitreCandidateView[] | null;
}

export function CaseStateMitreView({
  candidates,
}: CaseStateMitreViewProps) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xs font-extrabold uppercase tracking-wide text-ink">
          MITRE ATT&amp;CK Candidates
        </h3>
        <p className="mt-0.5 text-[11px] text-ink-secondary">
          External technique candidates mapped from threat activity claims for
          this round.
        </p>
      </div>

      {!candidates || candidates.length === 0 ? (
        <div className="space-y-2 rounded-xl border border-line bg-surface p-6 text-center">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-surface-hover text-ink-muted">
            <Icon name="report" className="h-5 w-5" />
          </div>
          <h4 className="text-xs font-extrabold text-ink">
            No MITRE Candidates for this Round
          </h4>
          <p className="mx-auto max-w-[260px] text-xs leading-relaxed text-ink-secondary">
            Technique candidates appear when technical analysis is completed and
            threat activity maps to ATT&amp;CK patterns.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {candidates.map((candidate) => (
            <article
              key={candidate.associationId}
              aria-label={`${candidate.techniqueId} MITRE candidate`}
              className="space-y-3 rounded-xl border border-[#D8D3E3] bg-surface p-4 shadow-2xs"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="rounded bg-[#EDE9F2] px-1.5 py-0.5 text-[9.5px] font-extrabold uppercase tracking-wide text-[#51495D]">
                    MITRE Candidate
                  </span>
                  <h4 className="mt-1.5 text-xs font-extrabold text-ink">
                    {candidate.techniqueId} — {candidate.techniqueName}
                  </h4>
                </div>
                <span className="font-mono text-[10px] font-bold text-ink-muted">
                  {candidate.associationId}
                </span>
              </div>

              {candidate.claims.length > 0 && (
                <div className="border-t border-line/60 pt-2.5">
                  <p className="text-[10px] font-bold uppercase tracking-wide text-ink-secondary">
                    Linked Analysis Claims ({candidate.claims.length})
                  </p>
                  <ul className="mt-1.5 space-y-1.5">
                    {candidate.claims.map((claim) => (
                      <li
                        key={claim.claimId}
                        className="rounded-lg bg-surface-hover/60 p-2 text-xs leading-relaxed text-ink-secondary"
                      >
                        <div className="mb-0.5 flex items-center gap-1.5">
                          <span className="rounded border border-line bg-surface px-1 py-0.2 font-mono text-[10px] font-bold text-ink">
                            {claim.claimId}
                          </span>
                          <span className="text-[9.5px] font-medium capitalize text-ink-muted">
                            {claim.claimType.replaceAll("_", " ")} · {claim.epistemicStatus}
                          </span>
                        </div>
                        <p className="text-xs text-ink">{claim.text}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {candidate.reason && (
                <div className="border-t border-line/60 pt-2.5">
                  <p className="text-[10px] font-bold uppercase tracking-wide text-ink-secondary">
                    Why this candidate?
                  </p>
                  <p className="mt-1 text-xs leading-relaxed text-ink-secondary">
                    {candidate.reason}
                  </p>
                </div>
              )}

              <div className="flex flex-wrap gap-1.5 pt-1 text-[9.5px] font-semibold text-[#665B73]">
                <span className="rounded-full border border-[#D8D3E3] bg-[#F7F5F9] px-2 py-0.5">
                  Candidate only
                </span>
                <span className="rounded-full border border-[#D8D3E3] bg-[#F7F5F9] px-2 py-0.5">
                  External technical context
                </span>
                <span className="rounded-full border border-[#D8D3E3] bg-[#F7F5F9] px-2 py-0.5">
                  Not incident evidence
                </span>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
