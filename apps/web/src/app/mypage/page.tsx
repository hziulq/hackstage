"use client";

import { useEffect, useState } from "react";
import { INTERNSHIP_INFO } from "@/lib/mock-data";
import type { Member } from "@/lib/types";
import { ApiError } from "@/lib/api";
import { calendarsClient, type ApiCalendar, type ApiCalendarMember } from "@/lib/calendars";
import { useGroupCalendarId } from "@/lib/group";
import RankingList from "@/components/mypage/RankingList";
import InviteCodeCard from "@/components/mypage/InviteCodeCard";
import InternshipList from "@/components/mypage/InternshipList";

const AVATAR_COLORS = ["#6366f1", "#ec4899", "#22c55e", "#f59e0b", "#0ea5e9", "#a855f7"];

function colorFor(userId: number) {
  return AVATAR_COLORS[userId % AVATAR_COLORS.length];
}

function toMember(m: ApiCalendarMember): Member {
  return {
    id: String(m.id),
    name: m.display_name,
    score: m.total_points,
    avatarColor: colorFor(m.user_id),
  };
}

export default function MyPage() {
  const [groupCalendarId, setGroupCalendarId] = useGroupCalendarId();
  const [calendar, setCalendar] = useState<ApiCalendar | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (groupCalendarId === null) {
        setCalendar(null);
        setMembers([]);
        return;
      }
      try {
        const [cal, apiMembers] = await Promise.all([
          calendarsClient.get(groupCalendarId),
          calendarsClient.members(groupCalendarId, "score"),
        ]);
        if (cancelled) return;
        setCalendar(cal);
        setMembers(apiMembers.map(toMember));
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "読み込みに失敗しました");
        if (err instanceof ApiError && err.status === 404) {
          // 参加していない(データ不整合)場合は所属状態をリセットする
          setGroupCalendarId(null);
        }
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [groupCalendarId, setGroupCalendarId]);

  async function handleCreateGroup(name: string) {
    try {
      const created = await calendarsClient.create(name);
      setGroupCalendarId(created.id ?? null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "グループの作成に失敗しました");
    }
  }

  async function handleJoinGroup(code: string): Promise<{ ok: boolean; message: string }> {
    try {
      const joined = await calendarsClient.join(code);
      setGroupCalendarId(joined.id ?? null);
      return { ok: true, message: `「${joined.name}」に参加しました` };
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        return { ok: false, message: "招待コードが見つかりません" };
      }
      return { ok: false, message: "参加に失敗しました" };
    }
  }

  return (
    <div className="space-y-5 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">マイページ / グループ管理</h1>
        <p className="text-xs text-[var(--color-muted)]">
          スコア・グループ・地域のインターン情報をまとめて確認
        </p>
      </header>

      {error && <p className="text-xs text-red-500">{error}</p>}

      {calendar && (
        <section className="space-y-2">
          <h2 className="text-sm font-bold">スコアランキング</h2>
          <RankingList members={members} />
        </section>
      )}

      <section className="space-y-2">
        <h2 className="text-sm font-bold">グループ管理</h2>
        <InviteCodeCard
          group={
            calendar
              ? { name: calendar.name ?? "", inviteCode: calendar.invite_code ?? null }
              : null
          }
          onCreate={handleCreateGroup}
          onJoin={handleJoinGroup}
        />
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-bold">地域別インターン情報</h2>
        <InternshipList items={INTERNSHIP_INFO} />
      </section>
    </div>
  );
}
