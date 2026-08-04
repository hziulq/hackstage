"use client";

import { useState } from "react";
import { REGIONS } from "@/lib/mock-data";
import type { InternshipInfo } from "@/lib/types";

export default function InternshipList({ items }: { items: InternshipInfo[] }) {
  const [region, setRegion] = useState<(typeof REGIONS)[number]>("すべて");

  const filtered = region === "すべて" ? items : items.filter((i) => i.region === region);

  return (
    <div className="space-y-3">
      <div className="scrollbar-none -mx-4 flex gap-1.5 overflow-x-auto px-4">
        {REGIONS.map((r) => (
          <button
            key={r}
            onClick={() => setRegion(r)}
            className={`shrink-0 rounded-full border px-3 py-1 text-xs font-medium ${
              region === r
                ? "border-[var(--color-brand)] bg-[var(--color-brand)] text-white"
                : "border-[var(--color-line)] text-[var(--color-muted)]"
            }`}
          >
            {r}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {filtered.map((info) => (
          <div key={info.id} className="card p-3">
            <div className="flex items-center justify-between">
              <span className="rounded-full bg-[var(--color-brand-2)]/10 px-2 py-0.5 text-[10px] font-semibold text-[var(--color-brand-2)]">
                {info.region}
              </span>
              <span className="text-[11px] text-[var(--color-muted)]">{info.period}</span>
            </div>
            <p className="mt-1.5 text-sm font-bold">{info.company}</p>
            <p className="text-xs text-[var(--color-muted)]">{info.title}</p>
            <div className="mt-1.5 flex flex-wrap gap-1">
              {info.tags.map((t) => (
                <span
                  key={t}
                  className="rounded-full bg-[var(--color-bg)] px-2 py-0.5 text-[10px] text-[var(--color-muted)]"
                >
                  #{t}
                </span>
              ))}
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="py-4 text-center text-xs text-[var(--color-muted)]">
            この地域の情報はまだありません
          </p>
        )}
      </div>
    </div>
  );
}
