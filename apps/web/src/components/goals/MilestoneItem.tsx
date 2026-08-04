"use client";

import { getMilestoneStatus, STATUS_COLOR, STATUS_LABEL } from "@/lib/milestones";
import type { Milestone } from "@/lib/types";

function formatMd(dateStr: string): string {
  const d = new Date(`${dateStr}T00:00:00`);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

export default function MilestoneItem({
  milestone,
  onToggle,
}: {
  milestone: Milestone;
  onToggle: (id: string) => void;
}) {
  const status = getMilestoneStatus(milestone);
  const color = STATUS_COLOR[status];

  return (
    <button
      onClick={() => onToggle(milestone.id)}
      className="flex w-full items-center gap-3 rounded-xl px-1 py-2 text-left"
    >
      <span
        className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 text-[11px] font-bold"
        style={{
          borderColor: color,
          background: milestone.done ? color : "transparent",
          color: milestone.done ? "#fff" : color,
        }}
      >
        {milestone.done ? "✓" : ""}
      </span>
      <span
        className={`flex-1 text-sm ${milestone.done ? "text-[var(--color-muted)] line-through" : ""}`}
      >
        {milestone.title}
      </span>
      <span className="text-xs text-[var(--color-muted)]">{formatMd(milestone.dueDate)}</span>
      <span
        className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
        style={{ background: `${color}1a`, color }}
      >
        {STATUS_LABEL[status]}
      </span>
    </button>
  );
}
