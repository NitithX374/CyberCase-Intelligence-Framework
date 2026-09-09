import { act, renderHook } from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";
import { useChatDraft } from "@/features/chat/workspace/use-chat-draft";

beforeEach(() => localStorage.clear());

it("restores drafts across case switches and remounts without exposing another account", () => {
  localStorage.setItem("cybercase:account", "account-a");
  const first = renderHook(() => useChatDraft());
  act(() => first.result.current.selectDraft("case-a"));
  act(() => first.result.current.changeInput("Private draft"));
  act(() => first.result.current.selectDraft("case-b"));
  expect(first.result.current.state.input).toBe("");
  act(() => first.result.current.selectDraft("case-a"));
  expect(first.result.current.state.input).toBe("Private draft");
  first.unmount();
  const second = renderHook(() => useChatDraft());
  act(() => second.result.current.selectDraft("case-a"));
  expect(second.result.current.state.input).toBe("Private draft");
  second.unmount();
  localStorage.setItem("cybercase:account", "account-b");
  const other = renderHook(() => useChatDraft());
  act(() => other.result.current.selectDraft("case-a"));
  expect(other.result.current.state.input).toBe("");
});
