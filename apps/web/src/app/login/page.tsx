import { Suspense } from "react";
import LoginForm from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <div className="space-y-4 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">ログイン</h1>
        <p className="text-xs text-[var(--color-muted)]">
          グループの仲間と進捗を共有しよう
        </p>
      </header>

      <Suspense>
        <LoginForm />
      </Suspense>
    </div>
  );
}
