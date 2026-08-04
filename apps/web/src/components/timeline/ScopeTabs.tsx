"use client";

export type Scope = "group" | "personal";

export default function ScopeTabs({
  scope,
  onChange,
  groupName,
}: {
  scope: Scope;
  onChange: (scope: Scope) => void;
  groupName: string;
}) {
  const tabs: { key: Scope; label: string }[] = [
    { key: "group", label: groupName },
    { key: "personal", label: "マイカレンダー" },
  ];

  return (
    <div className="flex gap-1 rounded-full bg-[var(--color-line)] p-1">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`flex-1 truncate rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
            scope === tab.key
              ? "bg-white text-[var(--color-brand)] shadow-sm"
              : "text-[var(--color-muted)]"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
