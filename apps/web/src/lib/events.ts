import { apiClient } from "./api";
import type { components } from "./api-types.generated";

export type ApiEvent = components["schemas"]["Event"];

/** events.py の /api/events。calendar_idの参加者本人のみ取得できる。 */
export const eventsClient = {
  list: (calendarId: number) => apiClient<ApiEvent[]>(`/events?calendar_id=${calendarId}`),
};
