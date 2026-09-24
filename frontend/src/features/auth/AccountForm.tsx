"use client";

import { useState, type FormEvent, type InputHTMLAttributes, type ReactNode } from "react";
import Link from "next/link";
import axios from "axios";
import { getApiBaseUrl, getApiErrorMessage, type UserProfile } from "@/lib/api";
import { CyberCaseLogo } from "@/components/CyberCaseLogo";
import { Icon } from "@/components/icons";

const MIN_PASSWORD_LENGTH = 8;

export function AccountForm({ register = false }: { register?: boolean }) {
  const [error, setError] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;
    const params = new URLSearchParams(window.location.search);
    if (!params.get("error")) return null;
    return "Authentication failed. Please check your credentials and try again.";
  });
  const [busy, setBusy] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const passwordLongEnough = password.length >= MIN_PASSWORD_LENGTH;
  const mismatch = register && confirmPassword.length > 0 && password !== confirmPassword;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (register) {
      if (!passwordLongEnough) {
        setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`);
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
    <main className="flex min-h-dvh items-center justify-center bg-surface px-5 py-12 text-ink">
      <section className="w-full max-w-sm">
        <div className="flex flex-col items-center text-center">
          <CyberCaseLogo size={40} />
          <h1 className="mt-5 text-2xl font-semibold tracking-[-0.02em] text-ink">
            {register ? "Create your account" : "Welcome back"}
          </h1>
        </div>

        <form
          onSubmit={submit}
          onChange={() => {
            if (error) setError(null);
          }}
          className="mt-8 space-y-4"
        >
          {register && (
            <Field id="auth-name-input" label="Name">
              <TextInput
                id="auth-name-input"
                name="name"
                autoComplete="name"
                required
                maxLength={255}
              />
            </Field>
          )}

          <Field id="auth-email-input" label="Email">
            <TextInput
              id="auth-email-input"
              name="email"
              type="email"
              autoComplete="email"
              required
              maxLength={254}
              placeholder="you@agency.go.th"
            />
          </Field>

          <Field
            id="auth-password-input"
            label="Password"
            hint={
              register ? (
                <span
                  className={`inline-flex items-center gap-1 ${passwordLongEnough ? "text-established" : ""}`}
                >
                  {passwordLongEnough && <Icon name="check" className="h-3.5 w-3.5" />}
                  At least {MIN_PASSWORD_LENGTH} characters
                </span>
              ) : undefined
            }
          >
            <PasswordInput
              id="auth-password-input"
              name="password"
              label="password"
              autoComplete={register ? "new-password" : "current-password"}
              minLength={register ? MIN_PASSWORD_LENGTH : 1}
              value={password}
              onChange={setPassword}
            />
          </Field>

          {register && (
            <Field
              id="auth-confirm-password-input"
              label="Confirm password"
              hint={
                mismatch ? <span className="text-critical">Passwords do not match</span> : undefined
              }
            >
              <PasswordInput
                id="auth-confirm-password-input"
                name="confirmPassword"
                label="confirm password"
                autoComplete="new-password"
                minLength={MIN_PASSWORD_LENGTH}
                value={confirmPassword}
                onChange={setConfirmPassword}
              />
            </Field>
          )}

          <div className="pt-2">
            <button type="submit" disabled={busy} className="btn-primary h-10 w-full">
              {busy && <Icon name="spinner" className="h-4 w-4" />}
              {busy
                ? register
                  ? "Creating account…"
                  : "Signing in…"
                : register
                  ? "Create account"
                  : "Sign in"}
            </button>
          </div>
        </form>

        {error && (
          <p
            role="alert"
            className="mt-4 rounded-lg bg-critical/[0.06] px-3 py-2.5 text-[13px] leading-5 text-critical"
          >
            {error}
          </p>
        )}

        <p className="mt-8 text-center text-[13px] text-ink-muted">
          {register ? "Already have an account? " : "New to CyberCase? "}
          <Link
            href={register ? "/login" : "/register"}
            className="font-semibold text-ink underline-offset-4 hover:underline"
          >
            {register ? "Sign in" : "Create an account"}
          </Link>
        </p>
      </section>
    </main>
  );
}

function Field({
  id,
  label,
  hint,
  children,
}: {
  id: string;
  label: string;
  hint?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div>
      <label htmlFor={id} className="block text-[13px] font-medium text-ink">
        {label}
      </label>
      <div className="mt-1.5">{children}</div>
      {hint && <p className="mt-1.5 text-xs text-ink-muted">{hint}</p>}
    </div>
  );
}

const inputClass =
  "h-10 w-full rounded-lg border border-line-strong bg-surface px-3 text-[15px] text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-ink";

function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={inputClass} />;
}

function PasswordInput({
  id,
  name,
  label,
  autoComplete,
  minLength,
  value,
  onChange,
}: {
  id: string;
  name: string;
  label: string;
  autoComplete: string;
  minLength: number;
  value: string;
  onChange: (value: string) => void;
}) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="relative">
      <input
        id={id}
        name={name}
        type={visible ? "text" : "password"}
        autoComplete={autoComplete}
        minLength={minLength}
        maxLength={128}
        required
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={`${inputClass} pr-10`}
      />
      <button
        type="button"
        tabIndex={-1}
        onClick={() => setVisible((current) => !current)}
        aria-label={`${visible ? "Hide" : "Show"} ${label}`}
        className="absolute inset-y-0 right-0 flex w-10 items-center justify-center text-ink-muted transition-colors hover:text-ink"
      >
        <Icon name={visible ? "eye-off" : "eye"} className="h-4 w-4" />
      </button>
    </div>
  );
}
