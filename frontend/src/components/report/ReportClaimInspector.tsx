import type { ChatReportClaim, ChatStructuredReport } from "@/lib/api";
import { caseReferenceAnchorId } from "@/lib/case-reference";

interface ReportClaimInspectorProps {
  claim: ChatReportClaim;
  sectionHeading: string;
  reportStatus: ChatStructuredReport["status"];
  threadId: string;
}

export function ReportClaimInspector({
  claim,
  sectionHeading,
  reportStatus,
  threadId,
}: ReportClaimInspectorProps) {
  return (
    <aside
      aria-label={`Claim inspector ${claim.claim_id}`}
      className="rounded-xl border border-line-strong bg-surface-nested p-4 lg:sticky lg:top-0 lg:self-start"
    >
      <p className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-ink-secondary">
        Claim inspector
      </p>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="text-sm font-extrabold text-ink">{claim.claim_id}</span>
        <span className="rounded-full border border-line-strong bg-surface px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.08em] text-ink-secondary">
          {readableValue(claim.support_type)}
        </span>
      </div>

      <InspectorField
        label="Section"
        value={`${sectionHeading} · ${claim.section_id}`}
      />
      <InspectorField label="Claim text" value={claim.text} />
      <InspectorField label="Support type" value={readableValue(claim.support_type)} />
      <ReferenceField
        label="Evidence"
        references={claim.evidence_ids}
        hrefForReference={(referenceId) =>
          `/chat/${encodeURIComponent(threadId)}/extraction#${caseReferenceAnchorId(referenceId)}`
        }
      />
      <ReferenceField label="Timeline" references={claim.timeline_event_ids} />
      <ReferenceField label="MITRE" references={claim.mitre_technique_ids} />
      <InspectorField label="Report status" value={readableValue(reportStatus)} />

      <p className="mt-4 border-t border-line pt-3 text-[11px] leading-5 text-ink-secondary">
        References expose persisted provenance. They do not independently verify
        this claim, and MITRE mappings remain external candidate context.
      </p>
    </aside>
  );
}

function InspectorField({ label, value }: { label: string; value: string }) {
  return (
    <div className="mt-4">
      <p className="text-[10px] font-extrabold uppercase tracking-[0.12em] text-ink-secondary">
        {label}
      </p>
      <p className="mt-1 text-xs leading-5 text-ink">{value}</p>
    </div>
  );
}

function ReferenceField({
  label,
  references,
  hrefForReference,
}: {
  label: string;
  references: string[];
  hrefForReference?: (referenceId: string) => string;
}) {
  return (
    <div className="mt-4">
      <p className="text-[10px] font-extrabold uppercase tracking-[0.12em] text-ink-secondary">
        {label}
      </p>
      {references.length === 0 ? (
        <p className="mt-1 text-xs text-ink-secondary">None</p>
      ) : (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {references.map((referenceId) =>
            hrefForReference ? (
              <a
                key={referenceId}
                href={hrefForReference(referenceId)}
                className="rounded-md border border-line-strong bg-surface px-2 py-1 text-[11px] font-bold text-ink outline-none transition-colors hover:border-primary focus-visible:ring-2 focus-visible:ring-primary"
              >
                {referenceId}
              </a>
            ) : (
              <span
                key={referenceId}
                className="rounded-md border border-line bg-surface px-2 py-1 text-[11px] font-bold text-ink-secondary"
              >
                {referenceId}
              </span>
            ),
          )}
        </div>
      )}
    </div>
  );
}

function readableValue(value: string): string {
  return value.replaceAll("_", " ");
}
