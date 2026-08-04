"use client";

import { useState } from "react";
import type { BoardPost } from "@/lib/types";

function relativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  if (hours < 1) return "たった今";
  if (hours < 24) return `${hours}時間前`;
  return `${Math.floor(hours / 24)}日前`;
}

export default function QuestionCard({
  post,
  onAddAnswer,
}: {
  post: BoardPost;
  onAddAnswer: (postId: string, body: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [draft, setDraft] = useState("");

  return (
    <div className="card p-4">
      <div className="flex flex-wrap gap-1">
        {post.tags.map((t) => (
          <span
            key={t}
            className="rounded-full bg-[var(--color-brand)]/10 px-2 py-0.5 text-[10px] font-semibold text-[var(--color-brand)]"
          >
            #{t}
          </span>
        ))}
      </div>

      <p className="mt-2 text-sm font-bold leading-snug">
        <span aria-hidden>Q. </span>
        {post.title}
      </p>
      <p className="mt-1 text-sm leading-relaxed text-[var(--color-ink)]/90">{post.body}</p>

      <div className="mt-2 flex items-center justify-between text-xs text-[var(--color-muted)]">
        <span>{relativeTime(post.createdAt)} ・ 匿名</span>
        <button
          onClick={() => setExpanded((v) => !v)}
          className="font-semibold text-[var(--color-brand)]"
        >
          回答 {post.answers.length}件{expanded ? " ▲" : " ▼"}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 space-y-2 border-t border-[var(--color-line)] pt-3">
          {post.answers.map((a) => (
            <div key={a.id} className="rounded-xl bg-[var(--color-bg)] px-3 py-2 text-sm">
              <span aria-hidden className="mr-1 font-semibold text-[var(--color-brand-2)]">
                A.
              </span>
              {a.body}
            </div>
          ))}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              const trimmed = draft.trim();
              if (!trimmed) return;
              onAddAnswer(post.id, trimmed);
              setDraft("");
            }}
            className="flex gap-2"
          >
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="回答を書く"
              className="flex-1 rounded-lg border border-[var(--color-line)] px-3 py-1.5 text-sm outline-none focus:border-[var(--color-brand)]"
            />
            <button
              type="submit"
              className="rounded-lg bg-[var(--color-brand)] px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-40"
              disabled={!draft.trim()}
            >
              送信
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
