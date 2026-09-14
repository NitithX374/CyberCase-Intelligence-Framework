"use client";

import { usePathname } from "next/navigation";
import { caseRouteState } from "@/features/chat/routing/workspaceRoutes";
import CaseShellLayout from "@/app/case/[caseId]/layout";
import IntakePage from "@/app/case/[caseId]/intake/page";
import OverviewPage from "@/app/case/[caseId]/overview/page";
import MaterialsPage from "@/app/case/[caseId]/materials/page";
import TechnicalContextPage from "@/app/case/[caseId]/technical-context/page";
import ReportPage from "@/app/case/[caseId]/report/page";

export function ChatWorkspace() {
  const pathname = usePathname();
  const routeState = caseRouteState(pathname);

  return (
    <CaseShellLayout>
      {routeState.view === "intake" ? (
        <IntakePage />
      ) : routeState.view === "materials" ? (
        <MaterialsPage />
      ) : routeState.view === "technical-context" ? (
        <TechnicalContextPage />
      ) : routeState.view === "report" ? (
        <ReportPage />
      ) : (
        <OverviewPage />
      )}
    </CaseShellLayout>
  );
}
