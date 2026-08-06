import { apiClient } from "./api";
import type { components } from "./api-types.generated";

export type ApiEvent = components["schemas"]["Event"];

/** events.py の /api/events。calendar_idの参加者本人のみ取得できる。 */
export const eventsClient = {
  list: (calendarId: number) => apiClient<ApiEvent[]>(`/events?calendar_id=${calendarId}`),

  create: (input: {
    calendarId: number;
    category: ApiEvent["category"];
    title: string;
    startAt: string;
    isPrivate?: boolean;
  }) =>
    apiClient<ApiEvent>("/events", {
      method: "POST",
      body: JSON.stringify({
        calendar_id: input.calendarId,
        category: input.category,
        title: input.title,
        start_at: input.startAt,
        is_private: input.isPrivate ?? false,
      }),
    }),
};
