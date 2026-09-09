"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import axios from "axios";
import { getApiBaseUrl, getApiErrorMessage, getOAuthLoginUrl, type UserProfile } from "@/lib/api";

export function AccountForm({ register = false }: { register?: boolean }) {
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [providers, setProviders] = useState<string[]>([]);
  useEffect(() => {
    const controller = new AbortController();
    axios.get<string[]>(`${getApiBaseUrl()}/auth/providers`, { signal: controller.signal })
      .then(({ data }) => setProviders(data))
      .catch((error: unknown) => { if (!axios.isCancel(error)) setError("Unable to load sign-in options."); });
    return () => controller.abort();
  }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      const { data } = await axios.post<UserProfile>(
        `${getApiBaseUrl()}/auth/${register ? "register" : "login"}`,
        { email: form.get("email"), password: form.get("password"), ...(register ? { name: form.get("name") } : {}) },
      );
      localStorage.setItem("cybercase:account", data.id);
      localStorage.setItem("cybercase:session-change", String(Date.now()));
      const route = localStorage.getItem(`cybercase:${data.id}:route`);
      window.location.assign(route?.startsWith("/chat/") ? route : "/chat");
    } catch (error) {
      setError(getApiErrorMessage(error, "Unable to sign in. Please try again."));
    } finally { setBusy(false); }
  }
  const inputClass = "mt-2 w-full rounded-lg border border-line bg-canvas px-3 py-3 text-ink focus:outline-2 focus:outline-ink";
  return <main className="flex min-h-screen items-center justify-center bg-canvas px-6 py-12 text-ink">
    <section className="w-full max-w-md rounded-2xl border border-line bg-surface p-8 shadow-sm">
      <p className="mb-8 text-sm font-bold tracking-widest">CYBERCASE</p>
      <h1 className="text-2xl font-semibold">{register ? "Create your account" : "Welcome back"}</h1>
      <p className="mt-2 mb-6 text-sm text-ink-secondary">{register ? "Keep your case work in your own workspace." : "Sign in to continue your case work."}</p>
      <form onSubmit={submit} className="space-y-4">
        {register && <label className="block text-sm">Name<input name="name" autoComplete="name" required maxLength={255} className={inputClass} /></label>}
        <label className="block text-sm">Email<input name="email" type="email" autoComplete="email" required maxLength={254} className={inputClass} /></label>
        <label className="block text-sm">Password<input name="password" type="password" autoComplete={register ? "new-password" : "current-password"} minLength={register ? 12 : 1} maxLength={128} required className={inputClass} /></label>
        {register && <p className="text-xs text-ink-secondary">Use at least 12 characters.</p>}
        <button disabled={busy} className="w-full rounded-lg bg-ink p-3 font-semibold text-canvas disabled:opacity-50">{busy ? "Please wait…" : register ? "Create account" : "Sign in"}</button>
      </form>
      {error && <p role="alert" className="mt-4 text-sm text-critical">{error}</p>}
      {providers.length > 0 && <div className="mt-6 space-y-2 border-t border-line pt-6">{providers.filter((provider): provider is "google" | "github" => provider === "google" || provider === "github").map(provider => <a key={provider} href={getOAuthLoginUrl(provider)} className="block rounded-lg border border-line p-3 text-center text-sm">Continue with {provider === "google" ? "Google" : "GitHub"}</a>)}</div>}
      <p className="mt-6 text-sm">{register ? "Already have an account? " : "New to CyberCase? "}<Link className="underline" href={register ? "/login" : "/register"}>{register ? "Sign in" : "Create account"}</Link></p>
    </section>
  </main>;
}
