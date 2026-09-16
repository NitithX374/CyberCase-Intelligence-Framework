import { describe, expect, it } from "vitest";

import {
  casePath,
  caseRouteState,
} from "@/lib/workspaceRoutes";

describe("Case workspace routes", () => {
  it("supports every current Case workspace view", () => {
    expect(caseRouteState("/case/case-1/intake")).toEqual({ caseId: "case-1", view: "intake" });
    expect(caseRouteState("/case/case-1/overview")).toEqual({ caseId: "case-1", view: "overview" });
    expect(caseRouteState("/case/case-1/materials")).toEqual({ caseId: "case-1", view: "materials" });
    expect(caseRouteState("/case/case-1/technical-context")).toEqual({ caseId: "case-1", view: "technical-context" });
    expect(caseRouteState("/case/case-1/report")).toEqual({ caseId: "case-1", view: "report" });
  });

  it("does not expose deleted extraction or relationship routes", () => {
    expect(caseRouteState("/case/caseChat-1/extraction")).toEqual({
      caseId: "caseChat-1",
      view: "overview",
    });
    expect(caseRouteState("/case/caseChat-1/relationships")).toEqual({
      caseId: "caseChat-1",
      view: "overview",
    });
    expect(casePath("caseChat-1", "overview")).toBe("/case/caseChat-1/overview");
  });

  it("treats non-Case paths as an unselected Case workspace", () => {
    expect(caseRouteState("/unknown/case-1/materials")).toEqual({ caseId: null, view: "overview" });
  });
});
