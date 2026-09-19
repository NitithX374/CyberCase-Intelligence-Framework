/**
 * Nothing is public except signing in.
 *
 * The front page was deleted and the root now redirects to /case, so the gate
 * is the only thing between a visitor and the workspace. It used to treat "/"
 * as public, which is the exemption that has to be gone.
 */

import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AccountGate } from "@/components/auth/AccountGate";
import { useAuth } from "@/hooks/useAuth";

const replace = vi.fn();
let pathname = "/case";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  usePathname: () => pathname,
}));

vi.mock("@/hooks/useAuth", () => ({ useAuth: vi.fn() }));

function signedOut() {
  vi.mocked(useAuth).mockReturnValue({
    user: null,
    isLoading: false,
    sessionError: null,
    refetchSession: vi.fn(),
  } as never);
}

function signedIn() {
  vi.mocked(useAuth).mockReturnValue({
    user: { id: "user-1" },
    isLoading: false,
    sessionError: null,
    refetchSession: vi.fn(),
  } as never);
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  pathname = "/case";
});

describe("a visitor who is not signed in", () => {
  it("is sent to login, with where they were going", async () => {
    pathname = "/case/abc/overview";
    signedOut();

    render(<AccountGate>workspace</AccountGate>);

    await waitFor(() =>
      expect(replace).toHaveBeenCalledWith("/login?redirect=%2Fcase%2Fabc%2Foverview"),
    );
    expect(screen.queryByText("workspace")).not.toBeInTheDocument();
  });

  it("is sent to login from the case library too", async () => {
    signedOut();
    render(<AccountGate>workspace</AccountGate>);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login?redirect=%2Fcase"));
  });

  it("can still reach the login page itself", () => {
    pathname = "/login";
    signedOut();

    render(<AccountGate>the form</AccountGate>);

    expect(screen.getByText("the form")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });
});

describe("a visitor who is signed in", () => {
  it("sees the workspace, and it remembers where they were", async () => {
    pathname = "/case/abc/report";
    signedIn();

    render(<AccountGate>workspace</AccountGate>);

    expect(screen.getByText("workspace")).toBeInTheDocument();
    await waitFor(() =>
      expect(localStorage.getItem("cybercase:user-1:route")).toBe("/case/abc/report"),
    );
  });

  it("is taken back to work if they land on the login page", async () => {
    pathname = "/login";
    localStorage.setItem("cybercase:user-1:route", "/case/abc/sources");
    signedIn();

    render(<AccountGate>the form</AccountGate>);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/case/abc/sources"));
  });

  it("goes to the library when there is nowhere remembered", async () => {
    pathname = "/login";
    signedIn();

    render(<AccountGate>the form</AccountGate>);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/case"));
  });
});

it("says so rather than guessing when the session cannot be checked", () => {
  vi.mocked(useAuth).mockReturnValue({
    user: null,
    isLoading: false,
    sessionError: new Error("unreachable"),
    refetchSession: vi.fn(),
  } as never);

  render(<AccountGate>workspace</AccountGate>);

  expect(screen.getByText("Unable to check your session.")).toBeInTheDocument();
  expect(replace).not.toHaveBeenCalled();
});
