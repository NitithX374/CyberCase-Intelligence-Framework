import { ChatMessageMarkdown } from "@/components/conversation/ChatMessageMarkdown";

interface WhatHappenedCardProps {
  summary: string;
  totalMessagesCount: number;
}

export function WhatHappenedCard({
  summary,
  totalMessagesCount,
}: WhatHappenedCardProps) {
  if (!summary) return null;

  return (
    <section aria-labelledby="overview-what-happened-heading" className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line pb-2.5">
        <div>
          <span className="font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase">
            01 / SUMMARY
          </span>
          <h2
            id="overview-what-happened-heading"
            className="text-base font-bold tracking-tight text-ink sm:text-lg"
          >
            What Happened? <span className="text-sm font-normal text-ink-secondary">· สรุปภาพรวมเหตุการณ์</span>
          </h2>
        </div>
        <span className="text-xs font-medium text-ink-muted">
          {totalMessagesCount} message{totalMessagesCount === 1 ? "" : "s"} in record
        </span>
      </div>

      <div className="text-sm leading-relaxed text-ink sm:text-[15px]">
        <ChatMessageMarkdown content={summary} />
      </div>
    </section>
  );
}
