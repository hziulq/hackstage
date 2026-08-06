"use client";

import { useState } from "react";

export default function NewPostBox({ onSubmit }: { onSubmit: (content: string) => void }) {
  const [content, setContent] = useState("");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const trimmed = content.trim();
        if (!trimmed) return;
        onSubmit(trimmed);
        setContent("");
      }}
      className="card flex items-end gap-2 p-3"
    >
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="進捗や気づきをシェアしよう"
        rows={1}
        className="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-[var(--color-muted)]"
      />
      <button
        type="submit"
        className="rounded-full bg-[var(--color-brand)] px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-40"
        disabled={!content.trim()}
      >
        投稿
      </button>
    </form>
  );
}
