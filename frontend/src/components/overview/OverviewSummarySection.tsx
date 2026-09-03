import { ChatMessageMarkdown } from "@/components/conversation/ChatMessageMarkdown";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";

export function OverviewSummarySection({ summary }: { summary: string }) {
  if (!summary) return null;

  return (
    <section aria-labelledby="overview-summary-heading" className="space-y-5">
      <WorkspaceSectionHeader
        headingId="overview-summary-heading"
        title={
          <>
            Case Summary
            <span className="ml-2 text-sm font-normal text-ink-secondary">
              · สรุปสาระสำคัญของสำนวน
            </span>
          </>
        }
      />
      <div className="max-w-prose text-sm leading-relaxed text-ink sm:text-[15px]">
        <ChatMessageMarkdown content={summary} />
      </div>
    </section>
  );
}
