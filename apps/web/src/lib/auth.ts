import { apiClient } from "./api";

/** GET /api/me のレスポンス（docs/design.md §7）。実際のフィールドは api 側の openapi.json に従う。 */
export interface Me {
  id: string;
  email: string;
  name: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

/** Client Component から呼ぶログイン/ログアウト/自分情報取得。 */
export const authClient = {
  login: (input: LoginInput) =>
    apiClient<Me>("/login", { method: "POST", body: JSON.stringify(input) }),
  logout: () => apiClient<void>("/logout", { method: "POST" }),
  me: () => apiClient<Me>("/me"),
};
