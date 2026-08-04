"use client";

import { useState } from "react";
import type { GroupInfo } from "@/lib/types";

export default function InviteCodeCard({ group }: { group: GroupInfo }) {
  const [copied, setCopied] = useState(false);
  const [joinCode, setJoinCode] = useState("");
  const [joinMessage, setJoinMessage] = useState<string | null>(null);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(group.inviteCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  function handleJoin(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = joinCode.trim().toUpperCase();
    if (!trimmed) return;
    if (trimmed === group.inviteCode) {
      setJoinMessage(`「${group.name}」に参加しました`);
    } else {
      setJoinMessage("招待コードが見つかりません");
    }
    setJoinCode("");
  }

  return (
    <div className="card space-y-4 p-4">
      <div>
        <p className="text-xs text-[var(--color-muted)]">所属グループ</p>
        <p className="text-sm font-bold">{group.name}</p>
      </div>

      <div>
        <p className="mb-1 text-xs text-[var(--color-muted)]">招待コード</p>
        <div className="flex items-center gap-2">
          <span className="flex-1 rounded-lg border border-dashed border-[var(--color-line)] px-3 py-2 text-center text-sm font-mono font-bold tracking-widest">
            {group.inviteCode}
          </span>
          <button
            onClick={handleCopy}
            className="rounded-lg bg-[var(--color-brand)] px-3 py-2 text-xs font-semibold text-white"
          >
            {copied ? "コピー済み" : "コピー"}
          </button>
        </div>
      </div>

      <form onSubmit={handleJoin} className="border-t border-[var(--color-line)] pt-3">
        <p className="mb-1 text-xs text-[var(--color-muted)]">招待コードで参加</p>
        <div className="flex gap-2">
          <input
            value={joinCode}
            onChange={(e) => {
              setJoinCode(e.target.value);
              setJoinMessage(null);
            }}
            placeholder="例：DINO-2027"
            className="flex-1 rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
          />
          <button
            type="submit"
            className="rounded-lg border border-[var(--color-brand)] px-3 py-2 text-xs font-semibold text-[var(--color-brand)]"
          >
            参加
          </button>
        </div>
        {joinMessage && (
          <p className="mt-1.5 text-xs text-[var(--color-muted)]">{joinMessage}</p>
        )}
      </form>
    </div>
  );
}
