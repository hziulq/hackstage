"use client";

import { useEffect, useRef, useState } from "react";

/**
 * localStorage に永続化する useState。
 * SSR ではサーバー描画と一致させるため initialValue をそのまま返し、
 * マウント後に一度だけ保存済みの値を読み込む（フロントエンド単体プロトタイプの簡易実装）。
 */
export function useLocalStorageState<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(initialValue);
  const hydrated = useRef(false);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(key);
      if (raw !== null) {
        setValue(JSON.parse(raw) as T);
      }
    } catch {
      // 破損データは無視して初期値を維持する
    } finally {
      hydrated.current = true;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  useEffect(() => {
    if (!hydrated.current) return;
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // ストレージ不可（プライベートモード等）は静かに諦める
    }
  }, [key, value]);

  return [value, setValue] as const;
}
