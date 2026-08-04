"use client";

import { calcProgress } from "@/lib/milestones";
import type { Goal } from "@/lib/types";
import ProgressMeter from "./ProgressMeter";
import MilestoneItem from "./MilestoneItem";

export default function GoalCard({
  goal,
  onToggleMilestone,
  onDelete,
}: {
  goal: Goal;
  onToggleMilestone: (goalId: string, milestoneId: string) => void;
  onDelete: (goalId: string) => void;
}) {
  const progress = calcProgress(goal.milestones);
  const target = new Date(`${goal.targetDate}T00:00:00`);

  return (
    <div className="card p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-bold">{goal.companyName}</p>
          <p className="text-xs text-[var(--color-muted)]">
            {goal.stage} ・ 目標日 {target.getMonth() + 1}/{target.getDate()}
          </p>
        </div>
        <button
          onClick={() => onDelete(goal.id)}
          className="text-xs text-[var(--color-muted)]"
          aria-label="ゴールを削除"
        >
          削除
        </button>
      </div>

      <div className="mt-3">
        <ProgressMeter progress={progress} />
      </div>

      <div className="mt-3 divide-y divide-[var(--color-line)]">
        {goal.milestones.map((m) => (
          <MilestoneItem
            key={m.id}
            milestone={m}
            onToggle={(milestoneId) => onToggleMilestone(goal.id, milestoneId)}
          />
        ))}
      </div>
    </div>
  );
}
