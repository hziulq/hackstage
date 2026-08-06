import { cookies } from "next/headers";
import { parseApiResponse } from "./api";

/**
 * Server Component / Server Action から呼ぶ。絶対URL + Cookie手動転送が必要
 * （docs/design.md §6。Server 側には fetch のオリジンが無いため相対パスは使えない）。
 */
export async function apiServer<T>(path: string, init?: RequestInit): Promise<T> {
  const apiInternalUrl = process.env.API_INTERNAL_URL;
  if (!apiInternalUrl) {
    throw new Error("API_INTERNAL_URL is not set");
  }

  const cookieStore = await cookies();
  const res = await fetch(`${apiInternalUrl}/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      cookie: cookieStore.toString(),
      ...init?.headers,
    },
    cache: "no-store",
  });
  return parseApiResponse<T>(res);
}
