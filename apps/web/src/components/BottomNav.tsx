"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/timeline", label: "タイムライン", icon: "📅" },
  { href: "/goals", label: "目標", icon: "🎯" },
  { href: "/board", label: "掲示板", icon: "💬" },
  { href: "/mypage", label: "マイページ", icon: "👤" },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 inset-x-0 z-40">
      <div className="app-shell !min-h-0">
        <div className="mx-3 mb-3 flex items-center justify-between rounded-2xl border border-[var(--color-line)] bg-white/95 px-2 py-2 shadow-lg backdrop-blur">
          {TABS.map((tab) => {
            const active = pathname?.startsWith(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`flex flex-1 flex-col items-center gap-0.5 rounded-xl py-1.5 text-[11px] font-medium transition-colors ${
                  active ? "text-[var(--color-brand)]" : "text-[var(--color-muted)]"
                }`}
              >
                <span
                  className={`text-lg leading-none ${active ? "" : "opacity-70"}`}
                  aria-hidden
                >
                  {tab.icon}
                </span>
                {tab.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
