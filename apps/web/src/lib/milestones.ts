import type { Milestone, MilestoneStatus } from "./types";

// 目標日から逆算した8つの標準マイルストーン（インターン/選考対策の一般的な流れ）
const MILESTONE_TEMPLATE: { offsetDays: number; title: string }[] = [
  { offsetDays: 60, title: "企業リサーチ・OB/OG訪問" },
  { offsetDays: 45, title: "自己分析・ES下書き開始" },
  { offsetDays: 30, title: "エントリーシート提出" },
  { offsetDays: 21, title: "Webテスト・適性検査対策" },
  { offsetDays: 14, title: "一次面接対策" },
  { offsetDays: 7, title: "二次面接対策" },
  { offsetDays: 3, title: "最終面接対策・身だしなみ確認" },
  { offsetDays: 0, title: "目標日" },
];

function toDateOnly(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function formatDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function generateMilestones(targetDate: string): Milestone[] {
  const target = toDateOnly(new Date(`${targetDate}T00:00:00`));

  return MILESTONE_TEMPLATE.map((tpl, index) => {
    const due = new Date(target);
    due.setDate(due.getDate() - tpl.offsetDays);
    return {
      id: `${targetDate}-${index}`,
      title: tpl.title,
      dueDate: formatDate(due),
      offsetDays: tpl.offsetDays,
      done: false,
    };
  });
}

export function getMilestoneStatus(milestone: Milestone, today = new Date()): MilestoneStatus {
  if (milestone.done) return "done";
  const todayStr = formatDate(toDateOnly(today));
  if (milestone.dueDate < todayStr) return "overdue";
  if (milestone.dueDate === todayStr) return "today";
  return "upcoming";
}

export function calcProgress(milestones: Milestone[]): number {
  if (milestones.length === 0) return 0;
  const done = milestones.filter((m) => m.done).length;
  return Math.round((done / milestones.length) * 100);
}

export function progressGradient(progress: number): string {
  if (progress >= 100) return "linear-gradient(90deg, #22c55e, #16a34a)";
  if (progress >= 60) return "linear-gradient(90deg, #84cc16, #22c55e)";
  if (progress >= 30) return "linear-gradient(90deg, #f59e0b, #84cc16)";
  return "linear-gradient(90deg, #ef4444, #f59e0b)";
}

export const STATUS_LABEL: Record<MilestoneStatus, string> = {
  done: "完了",
  overdue: "遅延",
  today: "今日",
  upcoming: "今後",
};

export const STATUS_COLOR: Record<MilestoneStatus, string> = {
  done: "#16a34a",
  overdue: "#ef4444",
  today: "#f59e0b",
  upcoming: "#94a3b8",
};
