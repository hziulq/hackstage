"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { authClient } from "@/lib/auth";
import { ApiError } from "@/lib/api";
import Skeleton from "@/components/ui/Skeleton";

export default function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const justRegistered = searchParams.get("registered") === "1";

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
      if (err instanceof ApiError && err.status === 429) {
        setError("試行回数が多すぎます。しばらく待ってから再試行してください");
      } else if (err instanceof ApiError) {
        // /api/login はメール不存在・パスワード誤りを区別しない一律の文言を返す
        // （docs/design.md §8）。ここではそのメッセージをそのまま表示する。
        setError(err.message);
      } else {
        setError("ログインに失敗しました");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-4 p-5">
      {justRegistered && (
        <p className="text-xs text-green-600">登録が完了しました。ログインしてください</p>
      )}

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
        className="flex w-full items-center justify-center rounded-xl bg-[var(--color-brand)] py-2.5 text-sm font-bold text-white disabled:opacity-60"
      >
        {submitting ? <Skeleton tone="onBrand" className="h-4 w-20" /> : "ログイン"}
      </button>

      <p className="text-center text-xs text-[var(--color-muted)]">
        アカウントが無い場合は{" "}
        <Link href="/register" className="font-medium text-[var(--color-brand)]">
          新規登録
        </Link>
      </p>
    </form>
  );
}
