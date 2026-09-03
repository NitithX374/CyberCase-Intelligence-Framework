import { ChatMessageMarkdown } from "@/components/conversation/ChatMessageMarkdown";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";

export function OverviewSummarySection({ summary }: { summary: string }) {
  if (!summary) return null;
  return (
    <section aria-labelledby="overview-summary-heading" className="order-1 min-w-0 space-y-4">
      <WorkspaceSectionHeader headingId="overview-summary-heading" title="Executive Summary" />
      <div className="max-w-prose text-sm leading-relaxed text-ink [overflow-wrap:anywhere] sm:text-[15px]">
        <ChatMessageMarkdown content={summary} />
      </div>
    </section>
  );
}
