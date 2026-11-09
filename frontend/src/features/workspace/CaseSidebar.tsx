"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CyberCaseLogo } from "@/components/CyberCaseLogo";
import { Icon, type IconName } from "@/components/icons";
import { useCaseOverview } from "@/features/analysis/useCaseOverview";
import { analysisPath, casePath } from "@/lib/casePaths";

interface NavItem {
  href: string;
  label: string;
  icon: IconName;
  count?: number;
  current: boolean;
}

export function CaseSidebar({
  caseId,
  caseTitle,
  compact = false,
}: {
  caseId: string;
  caseTitle: string;
  compact?: boolean;
}) {
  const pathname = usePathname() ?? "";
  const { overview, sources } = useCaseOverview(caseId);
  const analysis = analysisPath(caseId);
  const onFactPage = (section: string) => pathname.startsWith(`${analysis}/${section}`);
  const onReading =
    pathname.startsWith(analysis) &&
    !onFactPage("timeline") &&
    !onFactPage("people") &&
    !onFactPage("impact");
  const flagged = overview.findings.filter(
    (finding) => finding.traceability.semanticSupport === "not_supported",
  ).length;
  const total = overview.findings.length;
  const activeSources = sources?.filter((source) => !source.deactivated_at).length;

  const caseItems: NavItem[] = [
    { href: analysis, label: "Reading", icon: "findings", count: total, current: onReading },
    {
      href: analysisPath(caseId, "timeline"),
      label: "Timeline",
      icon: "timeline",
      count: overview.timeline.length,
      current: onFactPage("timeline"),
    },
    {
      href: analysisPath(caseId, "people"),
      label: "People",
      icon: "people",
      count: overview.parties.length,
      current: onFactPage("people"),
    },
    {
      href: analysisPath(caseId, "impact"),
      label: "Impact",
      icon: "impact",
      count: overview.impacts.length,
      current: onFactPage("impact"),
    },
    {
      href: `${analysis}#section-references`,
      label: "Outside references",
      icon: "references",
      current: false,
    },
  ];
  const materialItems: NavItem[] = [
    {
      href: casePath(caseId, "sources"),
      label: "Sources",
      icon: "sources",
      count: activeSources,
      current: pathname.startsWith(casePath(caseId, "sources")),
    },
    {
      href: casePath(caseId, "report"),
      label: "Report",
      icon: "report",
      current: pathname.startsWith(casePath(caseId, "report")),
    },
  ];

  return (
    <aside
      className={`hidden shrink-0 flex-col gap-1 overflow-y-auto bg-espresso py-6 text-espresso-ink transition-[width] duration-200 lg:flex ${
        compact ? "w-[4.5rem] px-2.5" : "w-[17.5rem] px-4"
      }`}
    >
      <Link
        href="/case"
        aria-label={compact ? "CyberCase, all cases" : undefined}
        className={`mb-5 flex items-center gap-3 rounded-lg text-xl font-bold tracking-[-0.01em] ${
          compact ? "justify-center" : "px-3"
        }`}
      >
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[10px] bg-surface">
          <CyberCaseLogo size={28} />
        </span>
        {!compact && "CyberCase"}
      </Link>

      <SidebarLink
        compact={compact}
        item={{ href: "/case", label: "All cases", icon: "folder", current: false }}
      />

      {compact ? (
        <span aria-hidden="true" className="mx-2 my-3 border-t border-espresso-line" />
      ) : (
        <p className="px-3.5 pt-5 pb-2 text-xs font-semibold tracking-[0.1em] text-espresso-muted uppercase">
          This case
        </p>
      )}
      <div
        className={`mb-1.5 rounded-[10px] border border-espresso-line bg-espresso-raised px-3.5 py-3 ${
          compact ? "hidden" : ""
        }`}
      >
        <p className="truncate text-sm font-semibold" title={caseTitle}>
          {caseTitle}
        </p>
        {overview.hasAnalysis ? (
          <>
            <div className="mt-2.5 h-1.5 overflow-hidden rounded-full bg-white/15">
              <div
                className="h-full rounded-full bg-primary-soft"
                style={{ width: `${total ? Math.round((flagged / total) * 100) : 0}%` }}
              />
            </div>
            <p className="mt-1.5 text-xs text-espresso-muted">
              {flagged === 0 ? "No findings to check" : `${flagged} of ${total} findings to check`}
            </p>
          </>
        ) : (
          <p className="mt-1 text-xs text-espresso-muted">Not analyzed yet</p>
        )}
      </div>
      <nav aria-label="Case pages" className="flex flex-col gap-1">
        {caseItems.map((item) => (
          <SidebarLink key={item.label} item={item} compact={compact} />
        ))}
      </nav>

      {compact ? (
        <span aria-hidden="true" className="mx-2 my-3 border-t border-espresso-line" />
      ) : (
        <p className="px-3.5 pt-5 pb-2 text-xs font-semibold tracking-[0.1em] text-espresso-muted uppercase">
          Material
        </p>
      )}
      <nav aria-label="Case material" className="flex flex-col gap-1">
        {materialItems.map((item) => (
          <SidebarLink key={item.label} item={item} compact={compact} />
        ))}
      </nav>
    </aside>
  );
}

function SidebarLink({ item, compact = false }: { item: NavItem; compact?: boolean }) {
  return (
    <Link
      href={item.href}
      onClick={() => {
        const id = item.href.split("#")[1];
        const target = id ? document.getElementById(id) : null;
        if (target instanceof HTMLDetailsElement) target.open = true;
        target?.scrollIntoView?.({ block: "start" });
      }}
      aria-current={item.current ? "page" : undefined}
      title={compact ? item.label : undefined}
      className={`flex min-h-11 items-center gap-3.5 rounded-lg text-sm transition-colors focus-visible:outline-white ${
        compact ? "justify-center px-0" : "px-3.5"
      } ${
        item.current
          ? "bg-primary font-semibold text-white"
          : "text-white/85 hover:bg-espresso-raised hover:text-white"
      }`}
    >
      <Icon name={item.icon} className="text-[22px]" />
      <span className={compact ? "sr-only" : undefined}>{item.label}</span>
      {!compact && item.count !== undefined && item.count > 0 && (
        <span
          className={`ml-auto inline-flex h-6 min-w-6 items-center justify-center rounded-md px-1.5 text-xs ${
            item.current ? "bg-white/20 text-white" : "bg-white/10 text-white/70"
          }`}
        >
          {item.count}
        </span>
      )}
    </Link>
  );
}
