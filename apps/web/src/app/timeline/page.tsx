"use client";

import { useEffect, useRef, useState } from "react";
import { useLocalStorageState } from "@/hooks/useLocalStorageState";
import { GROUP_INFO, INITIAL_EVENTS, INITIAL_TIMELINE_POSTS } from "@/lib/mock-data";
import type { CalendarEvent, ReactionKind, TimelinePost } from "@/lib/types";
import { authClient } from "@/lib/auth";
import { calendarsClient } from "@/lib/calendars";
import { eventsClient, type ApiEvent } from "@/lib/events";
import { postsClient, type ApiPost } from "@/lib/posts";
import { reactionsClient, type ApiReaction } from "@/lib/reactions";
import { ApiError } from "@/lib/api";
import ScopeTabs, { type Scope } from "@/components/timeline/ScopeTabs";
import ViewToggle, { type ViewMode } from "@/components/timeline/ViewToggle";
import UpcomingStrip from "@/components/timeline/UpcomingStrip";
import MonthCalendar from "@/components/timeline/MonthCalendar";
import PostCard from "@/components/timeline/PostCard";
import NewPostBox from "@/components/timeline/NewPostBox";

const KIND_TO_API: Record<ReactionKind, ApiReaction["kind"]> = {
  fire: "fire",
  thumbsUp: "thumbs_up",
  muscle: "muscle",
  party: "party",
};
const KIND_FROM_API: Record<ApiReaction["kind"], ReactionKind> = {
  fire: "fire",
  thumbs_up: "thumbsUp",
  muscle: "muscle",
  party: "party",
};

function toCalendarEvent(e: ApiEvent): CalendarEvent {
  const start = new Date(e.start_at);
  return {
    id: String(e.id),
    scope: "personal",
    title: e.title,
    date: `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, "0")}-${String(
      start.getDate()
    ).padStart(2, "0")}`,
    time: e.is_all_day
      ? undefined
      : `${String(start.getHours()).padStart(2, "0")}:${String(start.getMinutes()).padStart(2, "0")}`,
    location: e.location ?? undefined,
  };
}

function summarizeReactions(reactions: ApiReaction[], meId: number | null) {
  const counts: Record<ReactionKind, number> = { fire: 0, thumbsUp: 0, muscle: 0, party: 0 };
  let myReaction: ReactionKind | null = null;
  for (const r of reactions) {
    const kind = KIND_FROM_API[r.kind];
    counts[kind] += 1;
    if (meId !== null && r.user_id === meId) myReaction = kind;
  }
  return { counts, myReaction };
}

function toTimelinePost(p: ApiPost, reactions: ApiReaction[], meId: number | null): TimelinePost {
  const { counts, myReaction } = summarizeReactions(reactions, meId);
  return {
    id: String(p.id),
    scope: "personal",
    author: "自分",
    content: p.body,
    createdAt: p.created_at ?? new Date().toISOString(),
    reactions: counts,
    myReaction,
  };
}

export default function TimelinePage() {
  const [scope, setScope] = useState<Scope>("group");
  const [view, setView] = useState<ViewMode>("timeline");

  // group scope: これまでどおりモックデータ(ローカルストレージ)。
  const [groupEvents] = useLocalStorageState<CalendarEvent[]>("hackstage:events", INITIAL_EVENTS);
  const [groupPosts, setGroupPosts] = useLocalStorageState<TimelinePost[]>(
    "hackstage:posts",
    INITIAL_TIMELINE_POSTS
  );

  // personal scope: 個人カレンダー(calendars.mine)経由の実API。
  const [personalCalendarId, setPersonalCalendarId] = useState<number | null>(null);
  const [personalEvents, setPersonalEvents] = useState<CalendarEvent[]>([]);
  const [personalPosts, setPersonalPosts] = useState<TimelinePost[]>([]);
  const [loadingPersonal, setLoadingPersonal] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const meId = useRef<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoadingPersonal(true);
      setError(null);
      try {
        const me = await authClient.me();
        const calendar = await calendarsClient.mine();
        const [apiEvents, apiPosts] = await Promise.all([
          eventsClient.list(calendar.id!),
          postsClient.list({ category: "timeline", calendarId: calendar.id! }),
        ]);
        const posts = await Promise.all(
          apiPosts.map(async (p) => {
            const reactions = await reactionsClient.list("post", p.id!);
            return toTimelinePost(p, reactions, me.id ?? null);
          })
        );
        if (cancelled) return;
        meId.current = me.id ?? null;
        setPersonalCalendarId(calendar.id ?? null);
        setPersonalEvents(apiEvents.map(toCalendarEvent));
        setPersonalPosts(posts);
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "読み込みに失敗しました");
      } finally {
        if (!cancelled) setLoadingPersonal(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const scopedEvents = scope === "group" ? groupEvents.filter((e) => e.scope === "group") : personalEvents;
  const scopedPosts =
    scope === "group"
      ? groupPosts.filter((p) => p.scope === "group").sort((a, b) => b.createdAt.localeCompare(a.createdAt))
      : [...personalPosts].sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  function handleReactGroup(postId: string, kind: ReactionKind) {
    setGroupPosts((prev) =>
      prev.map((p) => {
        if (p.id !== postId) return p;
        const already = p.myReaction === kind;
        const reactions = { ...p.reactions };
        if (p.myReaction) reactions[p.myReaction] -= 1;
        if (!already) reactions[kind] += 1;
        return { ...p, reactions, myReaction: already ? null : kind };
      })
    );
  }

  async function handleReactPersonal(postId: string, kind: ReactionKind) {
    try {
      const current = await reactionsClient.list("post", Number(postId));
      const mine = current.find((r) => r.user_id === meId.current);
      if (mine && mine.kind === KIND_TO_API[kind]) {
        await reactionsClient.remove(mine.id!);
      } else {
        await reactionsClient.create({ targetType: "post", targetId: Number(postId), kind: KIND_TO_API[kind] });
      }
      const updated = await reactionsClient.list("post", Number(postId));
      const { counts, myReaction } = summarizeReactions(updated, meId.current);
      setPersonalPosts((prev) =>
        prev.map((p) => (p.id !== postId ? p : { ...p, reactions: counts, myReaction }))
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "リアクションに失敗しました");
    }
  }

  function handleReact(postId: string, kind: ReactionKind) {
    if (scope === "group") handleReactGroup(postId, kind);
    else handleReactPersonal(postId, kind);
  }

  function handleNewPostGroup(content: string) {
    const newPost: TimelinePost = {
      id: `p-${Date.now()}`,
      scope: "group",
      author: "自分",
      content,
      createdAt: new Date().toISOString(),
      reactions: { fire: 0, thumbsUp: 0, muscle: 0, party: 0 },
      myReaction: null,
    };
    setGroupPosts((prev) => [newPost, ...prev]);
  }

  async function handleNewPostPersonal(content: string) {
    if (personalCalendarId === null) return;
    try {
      const created = await postsClient.create({
        category: "timeline",
        body: content,
        calendarId: personalCalendarId,
      });
      setPersonalPosts((prev) => [toTimelinePost(created, [], meId.current), ...prev]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "投稿に失敗しました");
    }
  }

  function handleNewPost(content: string) {
    if (scope === "group") handleNewPostGroup(content);
    else handleNewPostPersonal(content);
  }

  return (
    <div className="space-y-4 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">タイムライン</h1>
        <p className="text-xs text-[var(--color-muted)]">
          仲間の進捗を確認して、今日やることを整えよう
        </p>
      </header>

      {error && <p className="text-xs text-red-500">{error}</p>}

      <ScopeTabs scope={scope} onChange={setScope} groupName={GROUP_INFO.name} />
      <UpcomingStrip events={scopedEvents} />
      <ViewToggle mode={view} onChange={setView} />

      {view === "calendar" ? (
        <MonthCalendar events={scopedEvents} />
      ) : (
        <div className="space-y-3">
          <NewPostBox onSubmit={handleNewPost} />
          {scope === "personal" && loadingPersonal ? (
            <p className="py-8 text-center text-sm text-[var(--color-muted)]">読み込み中...</p>
          ) : scopedPosts.length === 0 ? (
            <p className="py-8 text-center text-sm text-[var(--color-muted)]">
              まだ投稿がありません
            </p>
          ) : (
            scopedPosts.map((post) => (
              <PostCard key={post.id} post={post} onReact={handleReact} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
