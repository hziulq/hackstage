import { apiClient } from "./api";
import type { components } from "./api-types.generated";

/**
 * openapi.json（api が生成。憲章 原則V）から生成した型を使う。
 * 手書きしない。openapi.json が更新されたら
 * `npm run generate:api-types` で再生成する。
 */
export type User = components["schemas"]["User"];
export type LoginInput = components["schemas"]["Login"];
export type RegisterInput = components["schemas"]["Register"];

/** Client Component から呼ぶ登録/ログイン/ログアウト/自分情報取得。 */
export const authClient = {
  register: (input: RegisterInput) =>
    apiClient<User>("/register", { method: "POST", body: JSON.stringify(input) }),
  login: (input: LoginInput) =>
    apiClient<User>("/login", { method: "POST", body: JSON.stringify(input) }),
  logout: () => apiClient<void>("/logout", { method: "POST" }),
  me: () => apiClient<User>("/me"),
};
