"use client";

import { useLocalStorageState } from "@/hooks/useLocalStorageState";
import { GROUP_INFO, INITIAL_MEMBERS, INTERNSHIP_INFO } from "@/lib/mock-data";
import type { Member } from "@/lib/types";
import RankingList from "@/components/mypage/RankingList";
import InviteCodeCard from "@/components/mypage/InviteCodeCard";
import InternshipList from "@/components/mypage/InternshipList";

export default function MyPage() {
  const [members] = useLocalStorageState<Member[]>("hackstage:members", INITIAL_MEMBERS);

  return (
    <div className="space-y-5 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">マイページ / グループ管理</h1>
        <p className="text-xs text-[var(--color-muted)]">
          スコア・グループ・地域のインターン情報をまとめて確認
        </p>
      </header>

      <section className="space-y-2">
        <h2 className="text-sm font-bold">スコアランキング</h2>
        <RankingList members={members} />
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-bold">グループ管理</h2>
        <InviteCodeCard group={GROUP_INFO} />
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-bold">地域別インターン情報</h2>
        <InternshipList items={INTERNSHIP_INFO} />
      </section>
    </div>
  );
}
