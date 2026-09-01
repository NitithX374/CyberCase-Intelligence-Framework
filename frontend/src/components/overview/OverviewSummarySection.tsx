import { ChatMessageMarkdown } from "@/components/conversation/ChatMessageMarkdown";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";

export function OverviewSummarySection({ summary }: { summary: string }) {
  if (!summary) return null;

  return (
    <section aria-labelledby="overview-summary-heading" className="space-y-5">
      <WorkspaceSectionHeader
        eyebrow="01 / CASE SUMMARY"
        headingId="overview-summary-heading"
        title={
          <>
            What the Case Currently Says
            <span className="ml-2 text-sm font-normal text-ink-secondary">
              · สรุปสาระสำคัญของสำนวน
            </span>
          </>
        }
        description="A concise readout of what the submitted material currently supports."
      />
      <div className="max-w-prose text-sm leading-relaxed text-ink sm:text-[15px]">
        <ChatMessageMarkdown content={summary} />
      </div>
      <p className="border-l-2 border-evidence/40 pl-3 text-[11px] leading-relaxed text-ink-muted">
        This summary reflects submitted case material. It is not independent confirmation of every statement.
      </p>
    </section>
  );
}
