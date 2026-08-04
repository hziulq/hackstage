"use client";

import { progressGradient } from "@/lib/milestones";

export default function ProgressMeter({ progress }: { progress: number }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs text-[var(--color-muted)]">
        <span>達成度</span>
        <span className="font-semibold text-[var(--color-ink)]">{progress}%</span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-[var(--color-line)]">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${progress}%`, background: progressGradient(progress) }}
        />
      </div>
    </div>
  );
}
