"use client";

import { useState } from "react";

const STAGE_OPTIONS = ["ES提出", "Webテスト", "一次面接", "二次面接", "最終面接", "内定"];

export default function GoalForm({
  onCreate,
}: {
  onCreate: (input: { companyName: string; stage: string; targetDate: string }) => void;
}) {
  const [open, setOpen] = useState(false);
  const [companyName, setCompanyName] = useState("");
  const [stage, setStage] = useState(STAGE_OPTIONS[0]);
  const [targetDate, setTargetDate] = useState("");

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="card flex w-full items-center justify-center gap-1 py-3 text-sm font-semibold text-[var(--color-brand)]"
      >
        ＋ 新しいゴールを設定
      </button>
    );
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!companyName.trim() || !targetDate) return;
        onCreate({ companyName: companyName.trim(), stage, targetDate });
        setCompanyName("");
        setTargetDate("");
        setOpen(false);
      }}
      className="card space-y-3 p-4"
    >
      <p className="text-sm font-bold">ゴールを設定</p>

      <div>
        <label className="mb-1 block text-xs text-[var(--color-muted)]">企業名</label>
        <input
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="株式会社〇〇"
          className="w-full rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
          required
        />
      </div>

      <div>
        <label className="mb-1 block text-xs text-[var(--color-muted)]">選考ステージ</label>
        <select
          value={stage}
          onChange={(e) => setStage(e.target.value)}
          className="w-full rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
        >
          {STAGE_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="mb-1 block text-xs text-[var(--color-muted)]">目標日</label>
        <input
          type="date"
          value={targetDate}
          onChange={(e) => setTargetDate(e.target.value)}
          className="w-full rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]"
          required
        />
      </div>

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
          マイルストーンを生成
        </button>
      </div>
    </form>
  );
}
