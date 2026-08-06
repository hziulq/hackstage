import { apiClient } from "./api";
import type { components } from "./api-types.generated";

export type ApiCalendar = components["schemas"]["Calendar"];

/** calendars.py の /api/calendars。 */
export const calendarsClient = {
  /** 自分の個人カレンダーを取得する。無ければサーバー側で自動作成される。 */
  mine: () => apiClient<ApiCalendar>("/calendars/mine"),
};
