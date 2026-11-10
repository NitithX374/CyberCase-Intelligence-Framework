import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { AccountMenu } from "@/features/auth/AccountMenu";
import { useAuth } from "@/features/auth/useAuth";

vi.mock("@/features/auth/useAuth");
const logout = vi.fn().mockResolvedValue(undefined);
beforeEach(() => {
  vi.mocked(useAuth).mockReturnValue({
    user: null,
    sessionError: null,
    sessionFailures: 0,
    isLoading: false,
    logout,
    isLoggingOut: false,
    refetchSession: vi.fn(),
  });
});

function openMenu() {
  fireEvent.keyDown(screen.getByRole("button", { name: "Open account menu" }), { key: "Enter" });
  return screen.getByRole("menu");
}

it("links anonymous users to the login page", () => {
  render(<AccountMenu />);
  expect(within(openMenu()).getByRole("menuitem", { name: "Sign in" })).toHaveAttribute(
    "href",
    "/login",
  );
});

it("confirms before signing out the current account", async () => {
  vi.mocked(useAuth).mockReturnValue({
    ...useAuth(),
    user: {
      id: "u1",
      email: "a@example.com",
      name: "Analyst",
      created_at: "2026-09-09",
    },
  });
  render(<AccountMenu />);
  fireEvent.click(within(openMenu()).getByRole("menuitem", { name: "Sign out" }));
  await waitFor(() => {
    expect(screen.getByRole("heading", { name: "Sign out of CyberCase?" })).toBeInTheDocument();
  });
  fireEvent.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Sign out" }));
  await waitFor(() => expect(logout).toHaveBeenCalled());
});

it("runs an action from the menu", () => {
  const onSelect = vi.fn();
  vi.mocked(useAuth).mockReturnValue({
    ...useAuth(),
    user: { id: "u1", email: "a@example.com", name: "Analyst", created_at: "2026-09-09" },
  });
  render(<AccountMenu actions={[{ label: "New case", icon: "plus", onSelect }]} />);
  fireEvent.click(within(openMenu()).getByRole("menuitem", { name: "New case" }));
  expect(onSelect).toHaveBeenCalledOnce();
});
