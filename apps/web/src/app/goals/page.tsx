"use client";

import { useLocalStorageState } from "@/hooks/useLocalStorageState";
import { INITIAL_GOALS } from "@/lib/mock-data";
import { generateMilestones } from "@/lib/milestones";
import type { Goal } from "@/lib/types";
import GoalForm from "@/components/goals/GoalForm";
import GoalCard from "@/components/goals/GoalCard";

export default function GoalsPage() {
  const [goals, setGoals] = useLocalStorageState<Goal[]>("hackstage:goals", INITIAL_GOALS);

  function handleCreate(input: { companyName: string; stage: string; targetDate: string }) {
    const newGoal: Goal = {
      id: `g-${Date.now()}`,
      companyName: input.companyName,
      stage: input.stage,
      targetDate: input.targetDate,
      createdAt: new Date().toISOString(),
      milestones: generateMilestones(input.targetDate),
    };
    setGoals((prev) => [newGoal, ...prev]);
  }

  function handleToggleMilestone(goalId: string, milestoneId: string) {
    setGoals((prev) =>
      prev.map((g) =>
        g.id !== goalId
          ? g
          : {
              ...g,
              milestones: g.milestones.map((m) =>
                m.id === milestoneId ? { ...m, done: !m.done } : m
              ),
            }
      )
    );
  }

  function handleDelete(goalId: string) {
    setGoals((prev) => prev.filter((g) => g.id !== goalId));
  }

  return (
    <div className="space-y-4 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">目標＆逆算ToDo</h1>
        <p className="text-xs text-[var(--color-muted)]">
          目標日を決めると、8つのマイルストーンを自動で逆算します
        </p>
      </header>

      <GoalForm onCreate={handleCreate} />

      {goals.length === 0 ? (
        <p className="py-8 text-center text-sm text-[var(--color-muted)]">
          まだゴールが設定されていません
        </p>
      ) : (
        <div className="space-y-4">
          {goals.map((goal) => (
            <GoalCard
              key={goal.id}
              goal={goal}
              onToggleMilestone={handleToggleMilestone}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
