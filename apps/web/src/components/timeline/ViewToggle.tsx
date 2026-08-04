"use client";

export type ViewMode = "calendar" | "timeline";

export default function ViewToggle({
  mode,
  onChange,
}: {
  mode: ViewMode;
  onChange: (mode: ViewMode) => void;
}) {
  const options: { key: ViewMode; label: string; icon: string }[] = [
    { key: "calendar", label: "カレンダー", icon: "🗓️" },
    { key: "timeline", label: "タイムライン", icon: "📝" },
  ];

  return (
    <div className="grid grid-cols-2 gap-2">
      {options.map((opt) => (
        <button
          key={opt.key}
          onClick={() => onChange(opt.key)}
          className={`flex items-center justify-center gap-1.5 rounded-xl border py-2 text-sm font-semibold transition-colors ${
            mode === opt.key
              ? "border-[var(--color-brand)] bg-[var(--color-brand)]/10 text-[var(--color-brand)]"
              : "border-[var(--color-line)] text-[var(--color-muted)]"
          }`}
        >
          <span aria-hidden>{opt.icon}</span>
          {opt.label}
        </button>
      ))}
    </div>
  );
}
