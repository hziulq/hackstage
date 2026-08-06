"use client";

import { useState } from "react";

export default function InviteCodeCard({
  group,
  onCreate,
  onJoin,
}: {
  group: { name: string; inviteCode: string | null } | null;
  onCreate: (name: string) => Promise<void>;
  onJoin: (code: string) => Promise<{ ok: boolean; message: string }>;
}) {
  const [copied, setCopied] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [joinMessage, setJoinMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleCopy() {
    if (!group?.inviteCode) return;
    try {
      await navigator.clipboard.writeText(group.inviteCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = groupName.trim();
    if (!trimmed) return;
    setSubmitting(true);
    try {
      await onCreate(trimmed);
      setGroupName("");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleJoin(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = joinCode.trim();
    if (!trimmed) return;
    setSubmitting(true);
    try {
      const result = await onJoin(trimmed);
      setJoinMessage(result.message);
      if (result.ok) setJoinCode("");
    } finally {
      setSubmitting(false);
    }
  }

  if (!group) {
    return (
      <div className="card space-y-4 p-4">
        <form onSubmit={handleCreate} className="space-y-2">
          <p className="text-xs text-[var(--color-muted)]">グループを新しく作る</p>
          <div className="flex gap-2">
            <input
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              placeholder="グループ名（例：同期就活グループ）"
              className="flex-1 rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
            />
            <button
              type="submit"
              disabled={submitting || !groupName.trim()}
              className="rounded-lg bg-[var(--color-brand)] px-3 py-2 text-xs font-semibold text-white disabled:opacity-40"
            >
              作成
            </button>
          </div>
        </form>

        <form onSubmit={handleJoin} className="border-t border-[var(--color-line)] pt-3 space-y-2">
          <p className="text-xs text-[var(--color-muted)]">招待コードで参加する</p>
          <div className="flex gap-2">
            <input
              value={joinCode}
              onChange={(e) => {
                setJoinCode(e.target.value);
                setJoinMessage(null);
              }}
              placeholder="招待コードを入力"
              className="flex-1 rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
            />
            <button
              type="submit"
              disabled={submitting || !joinCode.trim()}
              className="rounded-lg border border-[var(--color-brand)] px-3 py-2 text-xs font-semibold text-[var(--color-brand)] disabled:opacity-40"
            >
              参加
            </button>
          </div>
          {joinMessage && <p className="text-xs text-[var(--color-muted)]">{joinMessage}</p>}
        </form>
      </div>
    );
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
    </div>
  );
}
