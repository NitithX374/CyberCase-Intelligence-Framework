import { describe, expect, it } from "vitest";

import { casePath, caseRouteState } from "./routes";

describe("Case workspace routes", () => {
  it("supports every current Case workspace view", () => {
    expect(caseRouteState("/case/case-1/sources")).toEqual({ caseId: "case-1", view: "sources" });
    expect(caseRouteState("/case/case-1/analysis")).toEqual({ caseId: "case-1", view: "analysis" });
    expect(caseRouteState("/case/case-1/legal")).toEqual({ caseId: "case-1", view: "legal" });
  });

  it("sends the views that were folded into Analysis there", () => {
    for (const retired of ["overview", "technical-context", "report"]) {
      expect(caseRouteState(`/case/case-1/${retired}`)).toEqual({
        caseId: "case-1",
        view: "analysis",
      });
    }
  });

  it("defaults unrecognised or missing view segments to analysis", () => {
    expect(caseRouteState("/case/case-1")).toEqual({
      caseId: "case-1",
      view: "analysis",
    });
    expect(caseRouteState("/case/case-1/unknown")).toEqual({
      caseId: "case-1",
      view: "analysis",
    });
    expect(casePath("case-1", "analysis")).toBe("/case/case-1/analysis");
  });

  it("treats non-Case paths as an unselected Case workspace", () => {
    expect(caseRouteState("/unknown/path")).toEqual({ caseId: null, view: "analysis" });
    expect(caseRouteState("/")).toEqual({ caseId: null, view: "analysis" });
  });

  it("encodes case identifiers properly in casePath", () => {
    expect(casePath("case #1", "sources")).toBe("/case/case%20%231/sources");
    expect(caseRouteState("/case/case%20%231/sources")).toEqual({
      caseId: "case #1",
      view: "sources",
    });
  });
});
