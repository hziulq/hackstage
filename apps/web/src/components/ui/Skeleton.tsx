const TONE_CLASS = {
  /** カード等、明るい背景の上で使う既定の色 */
  muted: "bg-[var(--color-line)]",
  /** ブランドカラーのボタン等、暗い背景の上で使う色 */
  onBrand: "bg-white/40",
} as const;

export default function Skeleton({
  className = "",
  tone = "muted",
}: {
  className?: string;
  tone?: keyof typeof TONE_CLASS;
}) {
  return (
    <div
      role="status"
      aria-label="読み込み中"
      className={`animate-pulse rounded-md ${TONE_CLASS[tone]} ${className}`}
    />
  );
}
