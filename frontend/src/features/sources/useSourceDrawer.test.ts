import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useSourceDrawer } from "./useSourceDrawer";
import type { SourceMessageRef } from "./types";

const sourceRef = { id: "source-1", label: "Case narrative #1" } as SourceMessageRef;
const citation = (key: string) => ({
  sourceRef,
  anchorElement: document.createElement("button"),
  key,
});

describe("useSourceDrawer", () => {
  it("opens a citation, and closes it when the same citation is pressed again", () => {
    const { result } = renderHook(() => useSourceDrawer());

    act(() => result.current.toggle(citation("finding-1")));
    expect(result.current.openKey).toBe("finding-1");

    act(() => result.current.toggle(citation("finding-1")));
    expect(result.current.open).toBeNull();
  });

  it("moves to another citation without closing first", () => {
    const { result } = renderHook(() => useSourceDrawer());

    act(() => result.current.toggle(citation("finding-1")));
    act(() => result.current.toggle(citation("finding-2")));
    expect(result.current.openKey).toBe("finding-2");

    act(() => result.current.close());
    expect(result.current.open).toBeNull();
  });
});
