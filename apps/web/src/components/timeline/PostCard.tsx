"use client";

import { REACTIONS, type ReactionKind, type TimelinePost } from "@/lib/types";

function relativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  if (hours < 1) return "たった今";
  if (hours < 24) return `${hours}時間前`;
  return `${Math.floor(hours / 24)}日前`;
}

export default function PostCard({
  post,
  onReact,
}: {
  post: TimelinePost;
  onReact: (postId: string, kind: ReactionKind) => void;
}) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold">{post.author}</span>
        <span className="text-xs text-[var(--color-muted)]">{relativeTime(post.createdAt)}</span>
      </div>
      <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{post.content}</p>
      <div className="mt-3 flex gap-1.5">
        {REACTIONS.map((r) => {
          const active = post.myReaction === r.kind;
          const count = post.reactions[r.kind];
          return (
            <button
              key={r.kind}
              onClick={() => onReact(post.id, r.kind)}
              className={`flex items-center gap-1 rounded-full border px-2 py-1 text-xs transition-colors ${
                active
                  ? "border-[var(--color-brand)] bg-[var(--color-brand)]/10"
                  : "border-[var(--color-line)]"
              }`}
            >
              <span aria-hidden>{r.emoji}</span>
              <span className="text-[var(--color-muted)]">{count}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
