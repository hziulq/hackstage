import { apiClient } from "./api";
import type { components } from "./api-types.generated";

export type ApiCalendar = components["schemas"]["Calendar"];

export interface ApiCalendarMember {
  id: number;
  user_id: number;
  role: "owner" | "member";
  joined_at: string | null;
  display_name: string;
  avatar_url: string | null;
  total_points: number;
}

/** calendars.py の /api/calendars。 */
export const calendarsClient = {
  /** 自分の個人カレンダーを取得する。無ければサーバー側で自動作成される。 */
  mine: () => apiClient<ApiCalendar>("/calendars/mine"),

  get: (calendarId: number) => apiClient<ApiCalendar>(`/calendars/${calendarId}`),

  members: (calendarId: number, sort?: "score") =>
    apiClient<ApiCalendarMember[]>(`/calendars/${calendarId}/members${sort ? `?sort=${sort}` : ""}`),

  /** グループカレンダーを新規作成する。作成者は自動的にownerとして参加する。 */
  create: (name: string) =>
    apiClient<ApiCalendar>("/calendars", { method: "POST", body: JSON.stringify({ name }) }),

  /** 招待コードでグループカレンダーに参加する。参加済みの場合もエラーにならない。 */
  join: (inviteCode: string) =>
    apiClient<ApiCalendar>("/calendars/join", {
      method: "POST",
      body: JSON.stringify({ invite_code: inviteCode }),
    }),
};
