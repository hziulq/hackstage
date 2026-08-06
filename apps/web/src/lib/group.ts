"use client";

import { useLocalStorageState } from "@/hooks/useLocalStorageState";

/**
 * 自分が所属している(最初に作成/参加した)グループカレンダーのidをブラウザに保持する。
 *
 * グループカレンダー一覧を返すAPIが無いため(research.md §5)、作成・参加時のレスポンスに
 * 含まれるidをここに保存し、以後`mypage`・`timeline`の両ページで共有する。別ブラウザ・
 * 別デバイスからは再取得できない制約が残ることを許容する(data-model.md参照)。
 */
export function useGroupCalendarId() {
  return useLocalStorageState<number | null>("hackstage:groupCalendarId", null);
}
