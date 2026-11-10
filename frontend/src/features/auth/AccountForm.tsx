"use client";

import { useState, type FormEvent, type InputHTMLAttributes, type ReactNode } from "react";
import Link from "next/link";
import { login, register as registerAccount } from "./api";
import { detailMessage } from "@/lib/userFacingError";
import { CyberCaseLogo } from "@/components/CyberCaseLogo";
import { Icon } from "@/components/icons";

const MIN_PASSWORD_LENGTH = 8;

export function AccountForm({ register = false }: { register?: boolean }) {
  const [error, setError] = useState<string | null>(null);
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
    const email = String(form.get("email") ?? "");
    try {
      const user = register
        ? await registerAccount({ email, password, name: String(form.get("name") ?? "") })
        : await login({ email, password });
      localStorage.setItem("cybercase:account", user.id);
      localStorage.setItem("cybercase:session-change", String(Date.now()));
      const route = localStorage.getItem(`cybercase:${user.id}:route`);
      window.location.assign(route?.startsWith("/case/") ? route : "/case");
    } catch (err) {
      setError(detailMessage(err, "Unable to sign in. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="grid min-h-dvh bg-surface text-ink lg:grid-cols-[minmax(0,1fr)_35rem]">
      <section className="ruled relative hidden flex-col overflow-hidden bg-primary px-14 py-12 text-white lg:flex">
        <span
          aria-hidden="true"
          className="pointer-events-none absolute -right-28 -bottom-28 opacity-[0.14] mix-blend-multiply"
        >
          <CyberCaseLogo size={460} />
        </span>
        <div className="relative flex items-center gap-3 text-2xl font-bold">
          <span className="flex h-11 w-11 items-center justify-center rounded-[10px] bg-surface">
            <CyberCaseLogo size={30} />
          </span>
          CyberCase
        </div>
        <div
          className="stagger relative mt-20 max-w-xl"
          style={{ ["--i" as string]: 1, ["--step" as string]: "90ms" }}
        >
          <p className="text-[44px] leading-[1.15] font-bold tracking-[-0.01em]">
            Every finding, next to the words it came from.
          </p>
          <p className="mt-4 text-lg leading-relaxed text-white/90">
            อ่านคดี ตรวจทุกข้อค้นพบกับถ้อยคำในเอกสารต้นทาง แล้วออกรายงาน
          </p>
        </div>
        <div
          aria-hidden="true"
          style={{ ["--i" as string]: 2, ["--step" as string]: "90ms" }}
          className="stagger relative mt-11 grid max-w-2xl grid-cols-[2.25rem_minmax(0,1fr)_15rem] gap-4 rounded-[10px] bg-surface p-5 text-ink shadow-[0_10px_30px_rgba(0,0,0,0.18)]"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-[9px] bg-primary text-sm font-bold text-white">
            2
          </span>
          <div>
            <p className="text-sm leading-6">
              The email said the account would be locked within one hour.
            </p>
            <span className="badge-check mt-2">Check against the source</span>
          </div>
          <p className="rounded-lg bg-surface-nested px-3 py-2.5 text-xs leading-5 text-ink-secondary">
            <span className="underline decoration-primary/70 underline-offset-3">
              It said the account would be locked unless the user signed in within one hour.
            </span>
          </p>
        </div>
        <ul className="relative mt-auto flex flex-wrap gap-x-7 gap-y-2 pt-10 text-sm text-white/85">
          <li>Thai and English sources</li>
          <li>PDF, Word and photos</li>
          <li>Report in PDF or HTML</li>
        </ul>
      </section>

      <section className="flex flex-col justify-center px-6 py-12 sm:px-16">
        <div className="rise-in mx-auto w-full max-w-sm">
          <div className="flex items-center gap-3 lg:hidden">
            <CyberCaseLogo size={36} />
            <span className="text-xl font-bold">CyberCase</span>
          </div>
          <h1 className="mt-6 text-3xl font-bold tracking-[-0.01em] text-ink lg:mt-0">
            {register ? "Create your account" : "Welcome back"}
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            {register ? "Set up an account to start a case." : "Sign in to open your cases."}
          </p>
          <nav
            aria-label="Account"
            className="mt-6 grid grid-cols-2 rounded-[10px] bg-surface-hover p-1 text-center text-sm"
          >
            <Link
              href="/login"
              aria-current={register ? undefined : "page"}
              className={`rounded-lg py-2.5 transition-[color,background-color,box-shadow] duration-150 ${register ? "text-ink-muted hover:text-ink" : "bg-surface font-semibold text-primary shadow-[0_2px_6px_rgba(24,24,28,0.08)]"}`}
            >
              Sign in
            </Link>
            <Link
              href="/register"
              aria-current={register ? "page" : undefined}
              className={`rounded-lg py-2.5 transition-[color,background-color,box-shadow] duration-150 ${register ? "bg-surface font-semibold text-primary shadow-[0_2px_6px_rgba(24,24,28,0.08)]" : "text-ink-muted hover:text-ink"}`}
            >
              Create account
            </Link>
          </nav>

          {error && (
            <p
              role="alert"
              className="mt-5 flex items-start gap-2 rounded-lg bg-critical/[0.07] px-3.5 py-3 text-sm leading-5 text-critical"
            >
              <Icon name="alert" className="mt-0.5 text-base" />
              {error}
            </p>
          )}

          <form
            onSubmit={submit}
            onChange={() => {
              if (error) setError(null);
            }}
            className="mt-6 space-y-4"
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
                  mismatch ? (
                    <span className="text-critical">Passwords do not match</span>
                  ) : undefined
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
              <button type="submit" disabled={busy} className="btn-primary h-12 w-full">
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
        </div>
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
      <label htmlFor={id} className="block text-sm font-medium text-ink">
        {label}
      </label>
      <div className="mt-1.5">{children}</div>
      {hint && <p className="mt-1.5 text-xs text-ink-muted">{hint}</p>}
    </div>
  );
}

const inputClass =
  "h-12 w-full rounded-lg border border-line-strong bg-surface px-3.5 text-base text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-primary focus:ring-4 focus:ring-primary/12";

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
        className="absolute inset-y-0 right-0 flex w-12 items-center justify-center text-ink-muted transition-colors hover:text-primary"
      >
        <Icon name={visible ? "eye-off" : "eye"} className="text-xl" />
      </button>
    </div>
  );
}
