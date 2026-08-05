"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth";
import { ApiError } from "@/lib/api";

export default function RegisterForm() {
  const router = useRouter();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      // register は自動ログインしない（api 側でセッションを発行しない実装のため）。
      // 登録後はログイン画面へ誘導する。
      await authClient.register({ display_name: displayName, email, password });
      router.push("/login?registered=1");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "登録に失敗しました");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-4 p-5">
      <div className="space-y-1.5">
        <label htmlFor="displayName" className="text-xs font-medium text-[var(--color-muted)]">
          表示名
        </label>
        <input
          id="displayName"
          type="text"
          required
          minLength={1}
          maxLength={100}
          autoComplete="name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          className="w-full rounded-xl border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
        />
      </div>

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
          パスワード（8文字以上）
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
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
        {submitting ? "登録中..." : "新規登録"}
      </button>

      <p className="text-center text-xs text-[var(--color-muted)]">
        アカウントをお持ちの場合は{" "}
        <Link href="/login" className="font-medium text-[var(--color-brand)]">
          ログイン
        </Link>
      </p>
    </form>
  );
}
