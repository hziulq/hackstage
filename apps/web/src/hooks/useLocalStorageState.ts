"use client";

import { useEffect, useState } from "react";

/**
 * localStorage に永続化する useState。
 * SSR ではサーバー描画と一致させるため initialValue をそのまま返し、
 * マウント後に一度だけ保存済みの値を読み込む（フロントエンド単体プロトタイプの簡易実装）。
 *
 * hydrated を ref ではなく state にしているのは、読み込み完了(setValue)と
 * 書き込み許可(hydrated=true)を同一レンダーで同期させるため。ref だと
 * 「読み込みエフェクト」が同期的に hydrated.current=true にした直後、
 * 同じコミット内で走る「書き込みエフェクト」が setValue の反映(再レンダー)を
 * 待たずに古い initialValue を書き込んでしまい、保存済みの値を一瞬 initialValue
 * で上書きしてしまう（React Strict Mode 下ではエフェクトが二重実行されるため
 * この上書きが最終値として残ってしまうことがある）。
 */
export function useLocalStorageState<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(initialValue);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(key);
      if (raw !== null) {
        setValue(JSON.parse(raw) as T);
      }
    } catch {
      // 破損データは無視して初期値を維持する
    } finally {
      setHydrated(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  useEffect(() => {
    if (!hydrated) return;
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // ストレージ不可（プライベートモード等）は静かに諦める
    }
  }, [key, value, hydrated]);

  return [value, setValue] as const;
}
