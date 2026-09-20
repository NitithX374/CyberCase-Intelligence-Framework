"use client";

import { useState, useEffect, type FormEvent } from "react";
import Link from "next/link";
import axios from "axios";
import { getApiBaseUrl, getApiErrorMessage, type UserProfile } from "@/lib/api";
import { CyberCaseLogo } from "@/components/common/CyberCaseLogo";

export function AccountForm({ register = false }: { register?: boolean }) {
  const [error, setError] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;
    const params = new URLSearchParams(window.location.search);
    const err = params.get("error");
    if (!err) return null;
    return "Authentication failed. Please check your credentials and try again.";
  });
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  useEffect(() => {
    if (!register) return;
    if (!confirmPassword) {
      if (error === "Passwords do not match.") {
        setError(null);
      }
      return;
    }
    if (password === confirmPassword) {
      if (error === "Passwords do not match.") {
        setError(null);
      }
    } else {
      setError("Passwords do not match.");
    }
  }, [register, password, confirmPassword, error]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (register) {
      if (password.length < 8) {
        setError("Password must be at least 8 characters.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    }
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      const { data } = await axios.post<UserProfile>(
        `${getApiBaseUrl()}/auth/${register ? "register" : "login"}`,
        {
          email: form.get("email"),
          password: form.get("password"),
          ...(register ? { name: form.get("name") } : {}),
        },
      );
      localStorage.setItem("cybercase:account", data.id);
      localStorage.setItem("cybercase:session-change", String(Date.now()));
      const route = localStorage.getItem(`cybercase:${data.id}:route`);
      window.location.assign(route?.startsWith("/case/") ? route : "/case");
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to sign in. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-canvas px-4 py-12 sm:px-6 lg:px-8 text-ink">
      {/* Background cyber accent glow & subtle grid pattern */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 h-96 w-[640px] rounded-full bg-accent/8 blur-[120px]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-40 left-1/2 -translate-x-1/2 h-80 w-[480px] rounded-full bg-primary/5 blur-[100px]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-40 [background-image:radial-gradient(var(--color-line)_1px,transparent_1px)] [background-size:24px_24px]"
      />

      {/* Elevated Centered Card */}
      <section className="relative w-full max-w-[430px] rounded-2xl border border-line bg-surface/95 p-6 shadow-xl backdrop-blur-md sm:p-8">
        {/* Top Accent Gradient Line */}
        <div
          aria-hidden="true"
          className="absolute inset-x-0 top-0 h-1 rounded-t-2xl bg-gradient-to-r from-accent via-accent-strong to-primary"
        />

        {/* Branding & Header */}
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-3 flex items-center justify-center rounded-xl border border-line bg-surface p-2 shadow-xs">
            <CyberCaseLogo size={36} />
          </div>
          <h1 className="mt-3 text-xl font-bold tracking-tight text-ink sm:text-2xl">
            {register ? "Create your workspace" : "Welcome back"}
          </h1>
          <p className="mt-1.5 max-w-xs text-xs text-ink-secondary">
            {register
              ? "Initialize your case analysis and investigative workspace."
              : "Sign in to continue your case work."}
          </p>
        </div>

        {/* Segmented Tab Switcher */}
        <div className="mb-6 grid grid-cols-2 rounded-lg bg-surface-nested p-1 text-xs font-semibold">
          <Link
            href="/login"
            className={`flex items-center justify-center rounded-md py-1.5 transition-colors ${!register
              ? "bg-surface text-ink shadow-xs"
              : "text-ink-secondary hover:text-ink"
              }`}
          >
            Sign in
          </Link>
          <Link
            href="/register"
            className={`flex items-center justify-center rounded-md py-1.5 transition-colors ${register
              ? "bg-surface text-ink shadow-xs"
              : "text-ink-secondary hover:text-ink"
              }`}
          >
            Create account
          </Link>
        </div>

        {/* Auth Form */}
        <form onSubmit={submit} className="space-y-4">
          {register && (
            <div className="space-y-1.5">
              <label htmlFor="auth-name-input" className="block text-xs font-semibold text-ink">
                Full name
              </label>
              <div className="relative">
                <div
                  aria-hidden="true"
                  className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-ink-muted"
                >
                  <i className="bx bx-user text-base" />
                </div>
                <input
                  id="auth-name-input"
                  name="name"
                  autoComplete="name"
                  required
                  maxLength={255}
                  placeholder="e.g. Alex Mercer"
                  className="h-10 w-full rounded-lg border border-line bg-surface pl-9 pr-3 text-xs text-ink placeholder:text-ink-muted outline-none transition hover:border-line-strong focus:border-accent focus:ring-2 focus:ring-accent/20"
                />
              </div>
            </div>
          )}

          <div className="space-y-1.5">
            <label htmlFor="auth-email-input" className="block text-xs font-semibold text-ink">
              Email address
            </label>
            <div className="relative">
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-ink-muted"
              >
                <i className="bx bx-envelope text-base" />
              </div>
              <input
                id="auth-email-input"
                name="email"
                type="email"
                autoComplete="email"
                required
                maxLength={254}
                placeholder="investigator@agency.gov"
                className="h-10 w-full rounded-lg border border-line bg-surface pl-9 pr-3 text-xs text-ink placeholder:text-ink-muted outline-none transition hover:border-line-strong focus:border-accent focus:ring-2 focus:ring-accent/20"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label htmlFor="auth-password-input" className="block text-xs font-semibold text-ink">
                Password
              </label>
              {register && (
                <span
                  className={`inline-flex items-center gap-1 text-[10px] font-medium transition-colors ${
                    password.length >= 8 ? "font-semibold text-accent" : "text-ink-muted"
                  }`}
                >
                  {password.length >= 8 ? (
                    <>
                      <i className="bx bx-check text-xs font-bold" />
                      <span>Valid (8+ chars)</span>
                    </>
                  ) : (
                    <span>Min. 8 chars ({password.length}/8)</span>
                  )}
                </span>
              )}
            </div>
            <div className="relative">
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-ink-muted"
              >
                <i className="bx bx-lock-alt text-base" />
              </div>
              <input
                id="auth-password-input"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete={register ? "new-password" : "current-password"}
                minLength={register ? 8 : 1}
                maxLength={128}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={register ? "Enter at least 8 characters" : "Enter your password"}
                className="h-10 w-full rounded-lg border border-line bg-surface pl-9 pr-10 text-xs text-ink placeholder:text-ink-muted outline-none transition hover:border-line-strong focus:border-accent focus:ring-2 focus:ring-accent/20"
              />
              <button
                type="button"
                tabIndex={-1}
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-ink-muted transition hover:text-ink focus:outline-none"
              >
                <i className={`bx ${showPassword ? "bx-hide" : "bx-show"} text-base`} />
              </button>
            </div>
          </div>

          {register && (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label
                  htmlFor="auth-confirm-password-input"
                  className="block text-xs font-semibold text-ink"
                >
                  Confirm password
                </label>
                {confirmPassword.length > 0 && (
                  <span
                    className={`inline-flex items-center gap-1 text-[10px] font-medium transition-colors ${
                      password === confirmPassword ? "font-semibold text-accent" : "text-critical"
                    }`}
                  >
                    {password === confirmPassword ? (
                      <>
                        <i className="bx bx-check text-xs font-bold" />
                        <span>Passwords match</span>
                      </>
                    ) : (
                      <span>Does not match</span>
                    )}
                  </span>
                )}
              </div>
              <div className="relative">
                <div
                  aria-hidden="true"
                  className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-ink-muted"
                >
                  <i className="bx bx-lock-alt text-base" />
                </div>
                <input
                  id="auth-confirm-password-input"
                  name="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  autoComplete="new-password"
                  minLength={8}
                  maxLength={128}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your password"
                  className="h-10 w-full rounded-lg border border-line bg-surface pl-9 pr-10 text-xs text-ink placeholder:text-ink-muted outline-none transition hover:border-line-strong focus:border-accent focus:ring-2 focus:ring-accent/20"
                />
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowConfirmPassword((prev) => !prev)}
                  aria-label={
                    showConfirmPassword ? "Hide confirm password" : "Show confirm password"
                  }
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-ink-muted transition hover:text-ink focus:outline-none"
                >
                  <i className={`bx ${showConfirmPassword ? "bx-hide" : "bx-show"} text-base`} />
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={busy}
            className="mt-2 flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-primary text-xs font-bold text-ivory shadow-xs transition hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-60"
          >
            {busy ? (
              <>
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory border-t-transparent" />
                <span>{register ? "Creating workspace…" : "Authenticating…"}</span>
              </>
            ) : (
              <>
                <span>{register ? "Create workspace" : "Sign in to workspace"}</span>
                <i className="bx bx-right-arrow-alt text-base" />
              </>
            )}
          </button>
        </form>

        {/* Error Alert */}
        {error && (
          <div
            role="alert"
            className="mt-4 flex items-start gap-2.5 rounded-lg border border-critical/30 bg-critical/5 p-3 text-xs text-critical"
          >
            <i className="bx bx-error-circle text-base text-critical shrink-0 mt-0.5" />
            <p className="flex-1 leading-snug">{error}</p>
          </div>
        )}
      </section>
    </main>
  );
}
