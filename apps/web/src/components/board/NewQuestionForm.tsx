"use client";

import { useState } from "react";

export default function NewQuestionForm({
  onCreate,
}: {
  onCreate: (input: { title: string; body: string; tags: string[] }) => void;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [tagsText, setTagsText] = useState("");

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="card flex w-full items-center justify-center gap-1 py-3 text-sm font-semibold text-[var(--color-brand)]"
      >
        ＋ 匿名で質問する
      </button>
    );
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!title.trim() || !body.trim()) return;
        const tags = tagsText
          .split(/[,、\s]+/)
          .map((t) => t.trim())
          .filter(Boolean);
        onCreate({ title: title.trim(), body: body.trim(), tags });
        setTitle("");
        setBody("");
        setTagsText("");
        setOpen(false);
      }}
      className="card space-y-3 p-4"
    >
      <p className="text-sm font-bold">匿名で質問する</p>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="タイトル（例：面接で聞かれたこと）"
        className="w-full rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
        required
      />
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder="質問の詳細"
        rows={3}
        className="w-full resize-none rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
        required
      />
      <input
        value={tagsText}
        onChange={(e) => setTagsText(e.target.value)}
        placeholder="タグ（スペース区切り 例：ES 面接）"
        className="w-full rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
      />
      <div className="flex gap-2 pt-1">
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="flex-1 rounded-lg border border-[var(--color-line)] py-2 text-sm font-medium text-[var(--color-muted)]"
        >
          キャンセル
        </button>
        <button
          type="submit"
          className="flex-1 rounded-lg bg-[var(--color-brand)] py-2 text-sm font-semibold text-white"
        >
          投稿する
        </button>
      </div>
    </form>
  );
}
