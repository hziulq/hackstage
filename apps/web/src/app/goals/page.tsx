"use client";

import { useEffect, useState } from "react";
import { goalsClient, type ApiGoal } from "@/lib/goals";
import { ApiError } from "@/lib/api";
import type { Goal } from "@/lib/types";
import GoalForm from "@/components/goals/GoalForm";
import GoalCard from "@/components/goals/GoalCard";

function toGoal(g: ApiGoal): Goal {
  return {
    id: String(g.id),
    companyName: g.company_name,
    stage: g.stage,
    targetDate: g.target_date,
    createdAt: g.created_at ?? new Date().toISOString(),
    milestones: (g.milestones ?? []).map((m) => ({
      id: String(m.id),
      title: m.title ?? "",
      dueDate: m.due_date ?? g.target_date,
      offsetDays: m.offset_days ?? 0,
      done: m.done ?? false,
    })),
  };
}

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    goalsClient
      .list()
      .then((apiGoals) => {
        if (!cancelled) setGoals(apiGoals.map(toGoal));
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "読み込みに失敗しました");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleCreate(input: { companyName: string; stage: string; targetDate: string }) {
    try {
      const created = await goalsClient.create(input);
      setGoals((prev) => [toGoal(created), ...prev]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "作成に失敗しました");
    }
  }

  async function handleToggleMilestone(goalId: string, milestoneId: string) {
    const goal = goals.find((g) => g.id === goalId);
    const milestone = goal?.milestones.find((m) => m.id === milestoneId);
    if (!goal || !milestone) return;

    try {
      await goalsClient.toggleMilestone(Number(goalId), Number(milestoneId), !milestone.done);
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
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "更新に失敗しました");
    }
  }

  async function handleDelete(goalId: string) {
    try {
      await goalsClient.remove(Number(goalId));
      setGoals((prev) => prev.filter((g) => g.id !== goalId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "削除に失敗しました");
    }
  }

  return (
    <div className="space-y-4 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">目標＆逆算ToDo</h1>
        <p className="text-xs text-[var(--color-muted)]">
          目標日を決めると、マイルストーンを自動で逆算します
        </p>
      </header>

      {error && <p className="text-xs text-red-500">{error}</p>}

      <GoalForm onCreate={handleCreate} />

      {loading ? (
        <p className="py-8 text-center text-sm text-[var(--color-muted)]">読み込み中...</p>
      ) : goals.length === 0 ? (
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
