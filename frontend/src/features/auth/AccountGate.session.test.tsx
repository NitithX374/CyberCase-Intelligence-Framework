import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { httpError, networkError } from "@/test/httpErrors";
import { AccountGate } from "./AccountGate";
import { authQueryKeys, useAuth } from "./useAuth";

const state = vi.hoisted(() => ({ getSession: vi.fn(), replace: vi.fn() }));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: state.replace }),
  usePathname: () => "/case/abc/sources",
}));
vi.mock("./api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./api")>()),
  getSession: (...args: unknown[]) => state.getSession(...args),
}));

const user = { id: "user-1", email: "analyst@example.com", name: "Analyst" };

function SessionCheck() {
  const { sessionError } = useAuth();
  return <p>{sessionError ? "Last check failed" : "Last check passed"}</p>;
}

function renderGate() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { refetchOnWindowFocus: false, staleTime: 15_000 } },
  });
  render(
    <QueryClientProvider client={queryClient}>
      <SessionCheck />
      <AccountGate>
        <label>
          Narrative
          <textarea />
        </label>
      </AccountGate>
    </QueryClientProvider>,
  );
  return queryClient;
}

beforeEach(() => {
  state.getSession.mockReset();
  state.replace.mockReset();
  localStorage.clear();
  localStorage.setItem("cybercase:account", user.id);
});

describe("a background session check that fails", () => {
  it.each([
    ["the network drops", networkError()],
    ["the backend answers 502", httpError(502, "Bad Gateway")],
  ])("keeps the workspace and what was typed when %s", async (_label, failure) => {
    state.getSession.mockResolvedValueOnce(user).mockRejectedValueOnce(failure);
    const queryClient = renderGate();
    const field = await screen.findByLabelText("Narrative");
    fireEvent.change(field, { target: { value: "half-written narrative" } });

    await act(() => queryClient.refetchQueries({ queryKey: authQueryKeys.session() }));
    expect(await screen.findByText("Last check failed")).toBeInTheDocument();

    expect(state.getSession).toHaveBeenCalledTimes(2);
    expect(screen.queryByText("Unable to check your session.")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Narrative")).toBe(field);
    expect(field).toHaveValue("half-written narrative");
    expect(state.replace).not.toHaveBeenCalled();
  });

  it("still says so when the first check fails, and sends no one to login", async () => {
    state.getSession.mockRejectedValue(networkError());
    renderGate();

    expect(await screen.findByText("Unable to check your session.")).toBeInTheDocument();
    expect(screen.queryByLabelText("Narrative")).not.toBeInTheDocument();
    expect(state.replace).not.toHaveBeenCalled();
  });
});
