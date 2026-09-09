import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { UserProfileMenu } from "@/components/common/UserProfileMenu";
import { useAuth } from "@/hooks/use-auth";

vi.mock("@/hooks/use-auth");
const logout = vi.fn().mockResolvedValue(undefined);
beforeEach(() => {
  vi.mocked(useAuth).mockReturnValue({
    user: null, sessionError: null, isLoading: false, isAuthenticated: false,
    devLogin: vi.fn(), isDevLoggingIn: false, logout, isLoggingOut: false,
    loginWithOAuth: vi.fn(), refetchSession: vi.fn(),
  });
});
it("links anonymous users to the login page", () => {
  render(<UserProfileMenu />);
  expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute("href", "/login");
});
it("signs out the current account", () => {
  vi.mocked(useAuth).mockReturnValue({ ...useAuth(), user: {
    id: "u1", email: "a@example.com", name: "Analyst", avatar_url: null,
    oauth_provider: "password", created_at: "2026-09-09",
  }});
  render(<UserProfileMenu />);
  fireEvent.click(screen.getByRole("button", { name: "Sign out" }));
  expect(logout).toHaveBeenCalled();
});
