import { apiClient } from "./api";
import type { components } from "./api-types.generated";

export type ApiPost = components["schemas"]["Post"];
export type ApiPostComment = components["schemas"]["PostComment"];

function toQueryString(params: Record<string, string | number | undefined>): string {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) qs.set(key, String(value));
  }
  const s = qs.toString();
  return s ? `?${s}` : "";
}

/** posts.py の /api/posts。掲示板・タイムラインの投稿を共通で扱う(006-openapi-generation)。 */
export const postsClient = {
  list: (params: {
    category?: ApiPost["category"];
    tag?: string;
    prefectureId?: number;
    calendarId?: number;
    scope?: "group" | "personal";
  }) =>
    apiClient<ApiPost[]>(
      `/posts${toQueryString({
        category: params.category,
        tag: params.tag,
        prefecture_id: params.prefectureId,
        calendar_id: params.calendarId,
        scope: params.scope,
      })}`
    ),

  create: (input: {
    category: ApiPost["category"];
    body: string;
    title?: string | null;
    tags?: string[] | null;
    calendarId?: number;
  }) =>
    apiClient<ApiPost>("/posts", {
      method: "POST",
      body: JSON.stringify({
        category: input.category,
        body: input.body,
        title: input.title ?? null,
        tags: input.tags ?? null,
        calendar_id: input.calendarId,
      }),
    }),

  listComments: (postId: number) => apiClient<ApiPostComment[]>(`/posts/${postId}/comments`),

  addComment: (postId: number, body: string) =>
    apiClient<ApiPostComment>(`/posts/${postId}/comments`, {
      method: "POST",
      body: JSON.stringify({ body }),
    }),
};
