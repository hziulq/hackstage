"use client";

import type { Member } from "@/lib/types";

const MEDALS = ["🥇", "🥈", "🥉"];

export default function RankingList({ members }: { members: Member[] }) {
  const sorted = [...members].sort((a, b) => b.score - a.score);

  return (
    <div className="card divide-y divide-[var(--color-line)]">
      {sorted.map((m, i) => (
        <div
          key={m.id}
          className={`flex items-center gap-3 px-4 py-3 ${
            m.name === "自分" ? "bg-[var(--color-brand)]/5" : ""
          }`}
        >
          <span className="w-5 text-center text-sm">{MEDALS[i] ?? i + 1}</span>
          <span
            className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white"
            style={{ background: m.avatarColor }}
          >
            {m.name.slice(0, 1)}
          </span>
          <span className="flex-1 text-sm font-medium">{m.name}</span>
          <span className="text-sm font-bold text-[var(--color-brand)]">{m.score}pt</span>
        </div>
      ))}
    </div>
  );
}
