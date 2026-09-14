"use client";

import { useState } from "react";
import Link from "next/link";
import { CyberCaseLogo } from "@/components/common/CyberCaseLogo";
import type { CaseRead } from "@/lib/api";
import { Icon, type IconName } from "@/components/common/icons";
import type { WorkspaceView } from "@/components/common/types";
import { WorkspaceCaseDrawer } from "./WorkspaceCaseDrawer";

interface WorkspaceNavigationProps {
  cases: CaseRead[];
  activeCaseId: string | null;
  casesLoading: boolean;
  casesError: string | null;
  onSelectCase: (caseId: string) => void;
  onNewCase: () => void;
  onRequestDelete: (caseRecord: CaseRead) => void;
  deletingCaseId: string | null;
  activeView: WorkspaceView;
  onViewChange: (view: WorkspaceView) => void;
}

const railDestinations: Array<{ view: WorkspaceView; label: string; icon: IconName }> = [
  { view: "overview", label: "Case analysis", icon: "overview" },
  { view: "materials", label: "Case materials", icon: "materials" },
  { view: "technical-context", label: "Technical context", icon: "technical" },
  { view: "report", label: "Case report", icon: "report" },
];

export function WorkspaceSidebar(props: WorkspaceNavigationProps) {
  const [isCaseDrawerOpen, setIsCaseDrawerOpen] = useState(false);

  const createCase = () => {
    props.onNewCase();
    setIsCaseDrawerOpen(false);
  };

  const selectCase = (caseId: string) => {
    props.onSelectCase(caseId);
    setIsCaseDrawerOpen(false);
  };

  return (
    <aside className="relative z-40 hidden h-full w-14 shrink-0 flex-col border-r border-line bg-sidebar md:flex">
      <Link
        href="/"
        aria-label="CyberCase home"
        title="CyberCase home"
        className="flex h-14 items-center justify-center border-b border-line outline-none hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent"
      >
        <CyberCaseLogo size={28} />
      </Link>

      <nav aria-label="Workspace shortcuts" className="flex flex-1 flex-col items-center gap-1.5 py-3">
        <RailButton label="New case" icon="plus" onClick={createCase} />
        <RailButton
          label="Cases"
          icon="materials"
          selected={isCaseDrawerOpen}
          expanded={isCaseDrawerOpen}
          controls="workspace-case-drawer"
          onClick={() => setIsCaseDrawerOpen((open) => !open)}
        />
        <span className="my-1 h-px w-7 bg-line" aria-hidden="true" />
        {railDestinations.map((item) => (
          <RailButton
            key={item.view}
            label={item.label}
            icon={item.icon}
            selected={!isCaseDrawerOpen && props.activeView === item.view}
            onClick={() => {
              props.onViewChange(item.view);
              setIsCaseDrawerOpen(false);
            }}
          />
        ))}
      </nav>

      <RailButton
        label="Account and cases"
        icon="account"
        selected={isCaseDrawerOpen}
        onClick={() => setIsCaseDrawerOpen(true)}
        className="mb-3"
      />

      <WorkspaceCaseDrawer
        isOpen={isCaseDrawerOpen}
        cases={props.cases}
        activeCaseId={props.activeCaseId}
        casesLoading={props.casesLoading}
        casesError={props.casesError}
        deletingCaseId={props.deletingCaseId}
        onClose={() => setIsCaseDrawerOpen(false)}
        onSelectCase={selectCase}
        onNewCase={createCase}
        onRequestDelete={props.onRequestDelete}
      />
    </aside>
  );
}

function RailButton({
  label,
  icon,
  selected = false,
  expanded,
  controls,
  className = "",
  onClick,
}: {
  label: string;
  icon: IconName;
  selected?: boolean;
  expanded?: boolean;
  controls?: string;
  className?: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      aria-expanded={expanded}
      aria-controls={controls}
      onClick={onClick}
      className={`mx-auto flex h-10 w-10 items-center justify-center rounded-md outline-none transition-colors focus-visible:ring-2 focus-visible:ring-accent ${
        selected ? "bg-accent-soft text-accent" : "text-ink-secondary hover:bg-surface-hover hover:text-ink"
      } ${className}`}
    >
      <Icon name={icon} className="h-[18px] w-[18px]" />
    </button>
  );
}
