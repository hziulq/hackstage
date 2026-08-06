"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import type { CalendarEvent, ReactionKind, TimelinePost } from "@/lib/types";
import { authClient } from "@/lib/auth";
import { calendarsClient } from "@/lib/calendars";
import { eventsClient, type ApiEvent } from "@/lib/events";
import { postsClient, type ApiPost } from "@/lib/posts";
import { reactionsClient, type ApiReaction } from "@/lib/reactions";
import { useGroupCalendarId } from "@/lib/group";
import { ApiError } from "@/lib/api";
import ScopeTabs, { type Scope } from "@/components/timeline/ScopeTabs";
import ViewToggle, { type ViewMode } from "@/components/timeline/ViewToggle";
import UpcomingStrip from "@/components/timeline/UpcomingStrip";
import MonthCalendar from "@/components/timeline/MonthCalendar";
import PostCard from "@/components/timeline/PostCard";
import NewPostBox from "@/components/timeline/NewPostBox";
import NewEventForm from "@/components/timeline/NewEventForm";

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

function toCalendarEvent(e: ApiEvent, scope: Scope): CalendarEvent {
  const start = new Date(e.start_at);
  return {
    id: String(e.id),
    scope,
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

function toTimelinePost(
  p: ApiPost,
  reactions: ApiReaction[],
  meId: number | null,
  scope: Scope,
  authorName: string
): TimelinePost {
  const { counts, myReaction } = summarizeReactions(reactions, meId);
  return {
    id: String(p.id),
    scope,
    author: authorName,
    content: p.body,
    createdAt: p.created_at ?? new Date().toISOString(),
    reactions: counts,
    myReaction,
  };
}

interface CalendarFeed {
  events: CalendarEvent[];
  posts: TimelinePost[];
}

const EMPTY_FEED: CalendarFeed = { events: [], posts: [] };

export default function TimelinePage() {
  const [scope, setScope] = useState<Scope>("group");
  const [view, setView] = useState<ViewMode>("timeline");
  const [error, setError] = useState<string | null>(null);
  const meId = useRef<number | null>(null);

  const [groupCalendarId, setGroupCalendarId] = useGroupCalendarId();
  const [personalCalendarId, setPersonalCalendarId] = useState<number | null>(null);

  const [groupFeed, setGroupFeed] = useState<CalendarFeed>(EMPTY_FEED);
  const [personalFeed, setPersonalFeed] = useState<CalendarFeed>(EMPTY_FEED);
  const [loadingGroup, setLoadingGroup] = useState(true);
  const [loadingPersonal, setLoadingPersonal] = useState(true);

  async function loadFeed(calendarId: number, scopeForFeed: Scope, nameFor: (userId: number) => string) {
    const [apiEvents, apiPosts] = await Promise.all([
      eventsClient.list(calendarId),
      postsClient.list({ category: "timeline", calendarId }),
    ]);
    const posts = await Promise.all(
      apiPosts.map(async (p) => {
        const reactions = await reactionsClient.list("post", p.id!);
        return toTimelinePost(p, reactions, meId.current, scopeForFeed, nameFor(p.user_id!));
      })
    );
    return { events: apiEvents.map((e) => toCalendarEvent(e, scopeForFeed)), posts };
  }

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoadingPersonal(true);
      setError(null);
      try {
        const me = await authClient.me();
        if (cancelled) return;
        meId.current = me.id ?? null;

        const calendar = await calendarsClient.mine();
        if (cancelled) return;
        setPersonalCalendarId(calendar.id ?? null);

        const feed = await loadFeed(calendar.id!, "personal", () => "自分");
        if (!cancelled) setPersonalFeed(feed);
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

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (groupCalendarId === null) {
        setGroupFeed(EMPTY_FEED);
        setLoadingGroup(false);
        return;
      }
      setLoadingGroup(true);
      try {
        const members = await calendarsClient.members(groupCalendarId);
        const nameByUserId = new Map(members.map((m) => [m.user_id, m.display_name]));
        const nameFor = (userId: number) =>
          userId === meId.current ? "自分" : nameByUserId.get(userId) ?? "メンバー";
        const feed = await loadFeed(groupCalendarId, "group", nameFor);
        if (!cancelled) setGroupFeed(feed);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "読み込みに失敗しました");
          if (err instanceof ApiError && err.status === 404) setGroupCalendarId(null);
        }
      } finally {
        if (!cancelled) setLoadingGroup(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupCalendarId]);

  const activeCalendarId = scope === "group" ? groupCalendarId : personalCalendarId;
  const activeFeed = scope === "group" ? groupFeed : personalFeed;
  const loading = scope === "group" ? loadingGroup : loadingPersonal;
  const scopedEvents = activeFeed.events;
  const scopedPosts = [...activeFeed.posts].sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  function applyReactionUpdate(postId: string, counts: Record<ReactionKind, number>, myReaction: ReactionKind | null) {
    const setFeed = scope === "group" ? setGroupFeed : setPersonalFeed;
    setFeed((prev) => ({
      ...prev,
      posts: prev.posts.map((p) => (p.id !== postId ? p : { ...p, reactions: counts, myReaction })),
    }));
  }

  async function handleReact(postId: string, kind: ReactionKind) {
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
      applyReactionUpdate(postId, counts, myReaction);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "リアクションに失敗しました");
    }
  }

  async function handleNewPost(content: string) {
    if (activeCalendarId === null) return;
    try {
      const created = await postsClient.create({
        category: "timeline",
        body: content,
        calendarId: activeCalendarId,
      });
      const setFeed = scope === "group" ? setGroupFeed : setPersonalFeed;
      const post = toTimelinePost(created, [], meId.current, scope, "自分");
      setFeed((prev) => ({ ...prev, posts: [post, ...prev.posts] }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "投稿に失敗しました");
    }
  }

  async function handleNewEvent(input: { title: string; date: string; time: string; category: string; isPrivate: boolean }) {
    if (activeCalendarId === null) return;
    try {
      const created = await eventsClient.create({
        calendarId: activeCalendarId,
        category: input.category as ApiEvent["category"],
        title: input.title,
        startAt: `${input.date}T${input.time}:00`,
        isPrivate: input.isPrivate,
      });
      const setFeed = scope === "group" ? setGroupFeed : setPersonalFeed;
      setFeed((prev) => ({ ...prev, events: [...prev.events, toCalendarEvent(created, scope)] }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "予定の作成に失敗しました");
    }
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

      <ScopeTabs scope={scope} onChange={setScope} groupName="グループ" />

      {scope === "group" && groupCalendarId === null ? (
        <p className="card px-4 py-6 text-center text-sm text-[var(--color-muted)]">
          まだグループに参加していません。
          <Link href="/mypage" className="ml-1 font-semibold text-[var(--color-brand)]">
            マイページ
          </Link>
          でグループを作成・参加してください。
        </p>
      ) : (
        <>
          <UpcomingStrip events={scopedEvents} />
          <ViewToggle mode={view} onChange={setView} />

          {view === "calendar" ? (
            <div className="space-y-3">
              <NewEventForm onCreate={handleNewEvent} />
              <MonthCalendar events={scopedEvents} />
            </div>
          ) : (
            <div className="space-y-3">
              <NewPostBox onSubmit={handleNewPost} />
              {loading ? (
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
        </>
      )}
    </div>
  );
}
