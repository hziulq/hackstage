"use client";

import { useMemo, useState } from "react";
import type { CalendarEvent } from "@/lib/types";

function ymd(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
    d.getDate()
  ).padStart(2, "0")}`;
}

export default function MonthCalendar({ events }: { events: CalendarEvent[] }) {
  const [cursor, setCursor] = useState(() => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1);
  });
  const [selected, setSelected] = useState(() => ymd(new Date()));

  const todayStr = ymd(new Date());

  const eventsByDate = useMemo(() => {
    const map = new Map<string, CalendarEvent[]>();
    for (const e of events) {
      const list = map.get(e.date) ?? [];
      list.push(e);
      map.set(e.date, list);
    }
    return map;
  }, [events]);

  const weeks = useMemo(() => {
    const firstDay = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
    const startOffset = firstDay.getDay();
    const gridStart = new Date(firstDay);
    gridStart.setDate(gridStart.getDate() - startOffset);

    const days: Date[] = [];
    for (let i = 0; i < 42; i++) {
      const d = new Date(gridStart);
      d.setDate(gridStart.getDate() + i);
      days.push(d);
    }
    const result: Date[][] = [];
    for (let i = 0; i < days.length; i += 7) {
      result.push(days.slice(i, i + 7));
    }
    return result;
  }, [cursor]);

  const selectedEvents = eventsByDate.get(selected) ?? [];

  return (
    <div className="card p-3">
      <div className="mb-2 flex items-center justify-between px-1">
        <button
          onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))}
          className="rounded-lg px-2 py-1 text-[var(--color-muted)]"
          aria-label="前の月"
        >
          ‹
        </button>
        <div className="text-sm font-semibold">
          {cursor.getFullYear()}年 {cursor.getMonth() + 1}月
        </div>
        <button
          onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))}
          className="rounded-lg px-2 py-1 text-[var(--color-muted)]"
          aria-label="次の月"
        >
          ›
        </button>
      </div>

      <div className="grid grid-cols-7 text-center text-[11px] text-[var(--color-muted)]">
        {["日", "月", "火", "水", "木", "金", "土"].map((w) => (
          <div key={w} className="py-1">
            {w}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-y-1 text-center text-sm">
        {weeks.flat().map((d, i) => {
          const key = ymd(d);
          const inMonth = d.getMonth() === cursor.getMonth();
          const hasEvents = eventsByDate.has(key);
          const isToday = key === todayStr;
          const isSelected = key === selected;
          return (
            <button
              key={i}
              onClick={() => setSelected(key)}
              className={`mx-auto flex h-8 w-8 flex-col items-center justify-center rounded-full ${
                isSelected
                  ? "bg-[var(--color-brand)] text-white"
                  : isToday
                  ? "border border-[var(--color-brand)] text-[var(--color-brand)]"
                  : inMonth
                  ? "text-[var(--color-ink)]"
                  : "text-[var(--color-muted)]/50"
              }`}
            >
              <span className="leading-none">{d.getDate()}</span>
              {hasEvents && (
                <span
                  className={`mt-0.5 h-1 w-1 rounded-full ${
                    isSelected ? "bg-white" : "bg-[var(--color-brand)]"
                  }`}
                />
              )}
            </button>
          );
        })}
      </div>

      <div className="mt-3 space-y-2 border-t border-[var(--color-line)] pt-3">
        {selectedEvents.length === 0 ? (
          <p className="text-center text-xs text-[var(--color-muted)]">
            この日の予定はありません
          </p>
        ) : (
          selectedEvents.map((e) => (
            <div key={e.id} className="flex items-center gap-2 text-sm">
              <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--color-brand)]" />
              <span className="font-medium">{e.title}</span>
              {e.time && <span className="text-xs text-[var(--color-muted)]">{e.time}</span>}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
