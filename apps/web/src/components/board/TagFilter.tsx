"use client";

export default function TagFilter({
  tags,
  active,
  onChange,
}: {
  tags: string[];
  active: string | null;
  onChange: (tag: string | null) => void;
}) {
  return (
    <div className="scrollbar-none -mx-4 flex gap-1.5 overflow-x-auto px-4">
      <button
        onClick={() => onChange(null)}
        className={`shrink-0 rounded-full border px-3 py-1 text-xs font-medium ${
          active === null
            ? "border-[var(--color-brand)] bg-[var(--color-brand)] text-white"
            : "border-[var(--color-line)] text-[var(--color-muted)]"
        }`}
      >
        すべて
      </button>
      {tags.map((tag) => (
        <button
          key={tag}
          onClick={() => onChange(tag)}
          className={`shrink-0 rounded-full border px-3 py-1 text-xs font-medium ${
            active === tag
              ? "border-[var(--color-brand)] bg-[var(--color-brand)] text-white"
              : "border-[var(--color-line)] text-[var(--color-muted)]"
          }`}
        >
          #{tag}
        </button>
      ))}
    </div>
  );
}
