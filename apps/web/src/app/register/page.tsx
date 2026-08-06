import RegisterForm from "@/components/auth/RegisterForm";

export default function RegisterPage() {
  return (
    <div className="space-y-4 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">新規登録</h1>
        <p className="text-xs text-[var(--color-muted)]">
          アカウントを作ってグループに参加しよう
        </p>
      </header>

      <RegisterForm />
    </div>
  );
}
