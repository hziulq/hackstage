"use client";

import type { CalendarEvent } from "@/lib/types";

function daysUntil(dateStr: string): number {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(`${dateStr}T00:00:00`);
  return Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

function formatShort(dateStr: string): { day: string; weekday: string } {
  const d = new Date(`${dateStr}T00:00:00`);
  return {
    day: String(d.getDate()),
    weekday: ["日", "月", "火", "水", "木", "金", "土"][d.getDay()],
  };
}

export default function UpcomingStrip({ events }: { events: CalendarEvent[] }) {
  const upcoming = [...events]
    .filter((e) => daysUntil(e.date) >= 0)
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(0, 6);

  if (upcoming.length === 0) {
    return (
      <div className="card px-4 py-3 text-sm text-[var(--color-muted)]">
        直近の予定はありません
      </div>
    );
  }

  return (
    <div className="scrollbar-none -mx-4 flex gap-2 overflow-x-auto px-4">
      {upcoming.map((e) => {
        const { day, weekday } = formatShort(e.date);
        const remain = daysUntil(e.date);
        return (
          <div
            key={e.id}
            className="card flex min-w-[104px] shrink-0 flex-col gap-1 px-3 py-2.5"
          >
            <div className="flex items-baseline gap-1 text-[var(--color-brand)]">
              <span className="text-lg font-bold leading-none">{day}</span>
              <span className="text-xs">{weekday}</span>
              <span className="ml-auto rounded-full bg-[var(--color-brand)]/10 px-1.5 py-0.5 text-[10px] font-semibold">
                {remain === 0 ? "今日" : `${remain}日後`}
              </span>
            </div>
            <div className="truncate text-xs font-medium">{e.title}</div>
            {e.time && <div className="text-[10px] text-[var(--color-muted)]">{e.time}</div>}
          </div>
        );
      })}
    </div>
  );
}
