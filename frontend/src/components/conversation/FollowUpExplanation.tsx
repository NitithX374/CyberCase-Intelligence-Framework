import type { ChatFollowUpGapDetail } from "@/lib/chat-followup";

interface FollowUpExplanationProps {
  detail: ChatFollowUpGapDetail;
}

export function FollowUpExplanation({ detail }: FollowUpExplanationProps) {
  return (
    <details className="mt-3 rounded-xl border border-line bg-surface-hover px-3.5 py-3 text-ink">
      <summary className="cursor-pointer text-xs font-extrabold text-ink marker:text-ink-secondary">
        Why is CyberCase asking this?
      </summary>
      <dl className="mt-3 grid gap-3 border-t border-line pt-3 text-xs leading-5">
        <div>
          <dt className="font-extrabold text-ink">Missing information</dt>
          <dd className="mt-0.5 text-ink-secondary">{detail.topic}</dd>
          <dd className="mt-0.5 text-ink-secondary">{detail.description}</dd>
        </div>
        <div>
          <dt className="font-extrabold text-ink">Why it matters</dt>
          <dd className="mt-0.5 text-ink-secondary">{detail.reason}</dd>
        </div>
        <div>
          <dt className="font-extrabold text-ink">Affected conclusion</dt>
          <dd className="mt-0.5 text-ink-secondary">{detail.affects}</dd>
        </div>
        <div className="flex items-center gap-2">
          <dt className="font-extrabold text-ink">Priority</dt>
          <dd className="rounded-full border border-line-strong bg-surface px-2 py-0.5 font-bold capitalize text-ink-secondary">
            {detail.priority}
          </dd>
        </div>
      </dl>
    </details>
  );
}
