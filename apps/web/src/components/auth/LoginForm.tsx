"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { authClient } from "@/lib/auth";
import { ApiError } from "@/lib/api";

export default function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await authClient.login({ email, password });
      const next = searchParams.get("next") ?? "/timeline";
      router.push(next);
      router.refresh();
    } catch (err) {
      // api の /api/login は成功・失敗の別以外を漏らさない一律の文言を返す想定
      // （docs/design.md §8）。ここではそのメッセージをそのまま表示する。
      setError(err instanceof ApiError ? err.message : "ログインに失敗しました");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-4 p-5">
      <div className="space-y-1.5">
        <label htmlFor="email" className="text-xs font-medium text-[var(--color-muted)]">
          メールアドレス
        </label>
        <input
          id="email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-xl border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
        />
      </div>

      <div className="space-y-1.5">
        <label htmlFor="password" className="text-xs font-medium text-[var(--color-muted)]">
          パスワード
        </label>
        <input
          id="password"
          type="password"
          required
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-xl border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
        />
      </div>

      {error && <p className="text-xs text-red-500">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-xl bg-[var(--color-brand)] py-2.5 text-sm font-bold text-white disabled:opacity-60"
      >
        {submitting ? "ログイン中..." : "ログイン"}
      </button>
    </form>
  );
}
