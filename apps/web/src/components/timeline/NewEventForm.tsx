"use client";

import { useState } from "react";

const CATEGORY_OPTIONS: { value: string; label: string }[] = [
  { value: "es", label: "ES提出" },
  { value: "written_test", label: "Webテスト" },
  { value: "group_discussion", label: "グループディスカッション" },
  { value: "interview", label: "面接" },
  { value: "info_session", label: "説明会" },
  { value: "offer", label: "内定" },
  { value: "other", label: "その他" },
];

export default function NewEventForm({
  onCreate,
}: {
  onCreate: (input: { title: string; date: string; time: string; category: string; isPrivate: boolean }) => void;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("10:00");
  const [category, setCategory] = useState(CATEGORY_OPTIONS[0].value);
  const [isPrivate, setIsPrivate] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="card flex w-full items-center justify-center gap-1 py-2.5 text-sm font-semibold text-[var(--color-brand)]"
      >
        ＋ 予定を追加
      </button>
    );
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!title.trim() || !date) return;
        onCreate({ title: title.trim(), date, time, category, isPrivate });
        setTitle("");
        setDate("");
        setIsPrivate(false);
        setOpen(false);
      }}
      className="card space-y-3 p-4"
    >
      <p className="text-sm font-bold">予定を追加</p>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="予定のタイトル"
        className="w-full rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
        required
      />
      <div className="flex gap-2">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="flex-1 rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
          required
        />
        <input
          type="time"
          value={time}
          onChange={(e) => setTime(e.target.value)}
          className="flex-1 rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
        />
      </div>
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="w-full rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
      >
        {CATEGORY_OPTIONS.map((c) => (
          <option key={c.value} value={c.value}>
            {c.label}
          </option>
        ))}
      </select>
      <label className="flex items-center gap-2 text-xs text-[var(--color-muted)]">
        <input
          type="checkbox"
          checked={isPrivate}
          onChange={(e) => setIsPrivate(e.target.checked)}
        />
        非公開にする(自分だけに表示)
      </label>
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
          追加する
        </button>
      </div>
    </form>
  );
}
