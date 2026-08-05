/**
 * api 契約のエラー形式（docs/design.md §7）:
 * 400 + { "error": { "code": "...", "message": "...", "fields": {...} } }
 */
export class ApiError extends Error {
  status: number;
  code?: string;
  fields?: Record<string, string>;

  constructor(status: number, message: string, code?: string, fields?: Record<string, string>) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}

export async function parseApiResponse<T>(res: Response): Promise<T> {
  if (res.ok) {
    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  }

  let body: { error?: { code?: string; message?: string; fields?: Record<string, string> } } = {};
  try {
    body = await res.json();
  } catch {
    // レスポンスボディが無い/JSONでない場合はそのまま既定メッセージを使う
  }

  throw new ApiError(
    res.status,
    body.error?.message ?? `API error (${res.status})`,
    body.error?.code,
    body.error?.fields
  );
}

/**
 * Client Component から呼ぶ。相対パス `/api/...` を叩く（docs/design.md §6）。
 * Cookie はブラウザが自動送信するため、ここでは扱わない。
 *
 * Server 側で使う場合は "@/lib/api.server" の apiServer を使うこと
 * （next/headers に依存するため、Client Component からは import できない）。
 */
export async function apiClient<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  return parseApiResponse<T>(res);
}
