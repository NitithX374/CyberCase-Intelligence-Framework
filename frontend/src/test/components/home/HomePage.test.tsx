import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import HomePage from "@/components/home/HomePage";
import * as api from "@/lib/api";

vi.mock("@/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api")>();
  return {
    ...actual,
    getSession: vi.fn().mockResolvedValue(null),
    logout: vi.fn().mockResolvedValue(undefined),
  };
});

describe("HomePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("sends the case entry point directly to the persistent chat workspace when logged out", () => {
    render(<HomePage />);

    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute(
      "href",
      "/login",
    );
    expect(
      screen.getByRole("link", { name: "Start new case" }),
    ).toHaveAttribute("href", "/case");
    const openChatLinks = screen.getAllByRole("link", { name: "Open chat" });
    expect(openChatLinks).toHaveLength(1);
    for (const link of openChatLinks) {
      expect(link).toHaveAttribute("href", "/case");
    }
  });

  it("renders user avatar placeholder and toggles dropdown with full name and log out when logged in", async () => {
    vi.mocked(api.getSession).mockResolvedValueOnce({
      id: "u123",
      name: "Kritsakorn Analyst",
      email: "analyst@example.com",
      created_at: "2026-09-09",
      oauth_provider: "password",
    });

    render(<HomePage />);

    await waitFor(() => {
      expect(
        screen.getByRole("link", { name: "Go to Workspace" }),
      ).toBeInTheDocument();
    });

    // Dropdown is closed initially
    expect(screen.queryByText("Kritsakorn Analyst")).not.toBeInTheDocument();

    // Click avatar button to open dropdown
    const avatarButton = screen.getByRole("button", {
      name: "User account menu",
    });
    await act(async () => {
      fireEvent.click(avatarButton);
    });

    // Full name and email are displayed in the dropdown
    expect(screen.getByText("Kritsakorn Analyst")).toBeInTheDocument();
    expect(screen.getByText("analyst@example.com")).toBeInTheDocument();

    // Log out button exists
    const logoutButton = screen.getByRole("menuitem", { name: "Log out" });
    expect(logoutButton).toBeInTheDocument();

    // Open the sign-out confirmation
    await act(async () => {
      fireEvent.click(logoutButton);
    });

    expect(
      screen.getByRole("heading", { name: "Sign out of CyberCase?" }),
    ).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(
        within(screen.getByRole("dialog")).getByRole("button", {
          name: "Sign out",
        }),
      );
    });
    expect(api.logout).toHaveBeenCalled();
  });
});
