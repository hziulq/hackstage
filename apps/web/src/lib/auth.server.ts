import { apiServer } from "./api.server";
import type { Me } from "./auth";

/** Server Component / Server Action から呼ぶ自分情報取得（Cookie 手動転送込み）。 */
export function getMe() {
  return apiServer<Me>("/me");
}
