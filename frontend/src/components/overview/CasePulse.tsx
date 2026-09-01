import type { PersistedChatMessage } from "@/lib/api";
import { Icon, type IconName } from "@/components/common/icons";
import { buildCaseMaterials } from "@/lib/case-materials";

interface CasePulseProps {
  messages: PersistedChatMessage[];
  findingCount: number;
  openQuestionCount: number;
  hasAnalysis: boolean;
}

interface PulseMetricProps {
  icon: IconName;
  label: string;
  value: string;
  detail: string;
}

export function CasePulse({
  messages,
  findingCount,
  openQuestionCount,
  hasAnalysis,
}: CasePulseProps) {
  const materialCount = buildCaseMaterials(messages).totalCount;
  const reportValue = hasAnalysis ? "Ready" : "Pending";
  const reportDetail = hasAnalysis
    ? "Can be generated from this analysis"
    : "Available after analysis completes";

  return (
    <section
      aria-label="Case at a glance"
      className="workspace-card overflow-hidden"
    >
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3 sm:px-5">
        <div>
          <p className="section-eyebrow">CASE PULSE</p>
          <h2 className="mt-1 text-sm font-extrabold tracking-tight text-ink">
            At a glance
          </h2>
        </div>
        <span className="text-[10px] font-medium text-ink-muted">Review snapshot</span>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 lg:divide-x lg:divide-line">
        <PulseMetric
          icon="materials"
          label="Submitted material"
          value={String(materialCount)}
          detail="User-provided case items"
        />
        <PulseMetric
          icon="overview"
          label="Findings"
          value={String(findingCount)}
          detail="Evidence-labelled readout"
        />
        <PulseMetric
          icon="alert"
          label="Needs attention"
          value={String(openQuestionCount)}
          detail={
            openQuestionCount === 0
              ? "No structured gaps recorded"
              : "Open analysis questions"
          }
        />
        <PulseMetric
          icon="report"
          label="Report"
          value={reportValue}
          detail={reportDetail}
        />
      </div>
    </section>
  );
}

function PulseMetric({ icon, label, value, detail }: PulseMetricProps) {
  return (
    <div className="flex min-h-24 items-start gap-3 border-b border-line px-4 py-4 last:border-b-0 sm:px-5 lg:border-b-0">
      <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-surface-nested text-ink-secondary">
        <Icon name={icon} className="h-3.5 w-3.5" />
      </span>
      <div className="min-w-0">
        <p className="text-[10px] font-bold uppercase tracking-[0.08em] text-ink-muted">
          {label}
        </p>
        <p className="mt-1 text-lg font-extrabold leading-none tracking-tight text-ink">
          {value}
        </p>
        <p className="mt-1 text-[10px] leading-4 text-ink-secondary">{detail}</p>
      </div>
    </div>
  );
}
