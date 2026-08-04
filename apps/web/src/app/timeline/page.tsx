"use client";

import { useState } from "react";
import { useLocalStorageState } from "@/hooks/useLocalStorageState";
import { GROUP_INFO, INITIAL_EVENTS, INITIAL_TIMELINE_POSTS } from "@/lib/mock-data";
import type { CalendarEvent, ReactionKind, TimelinePost } from "@/lib/types";
import ScopeTabs, { type Scope } from "@/components/timeline/ScopeTabs";
import ViewToggle, { type ViewMode } from "@/components/timeline/ViewToggle";
import UpcomingStrip from "@/components/timeline/UpcomingStrip";
import MonthCalendar from "@/components/timeline/MonthCalendar";
import PostCard from "@/components/timeline/PostCard";
import NewPostBox from "@/components/timeline/NewPostBox";

export default function TimelinePage() {
  const [scope, setScope] = useState<Scope>("group");
  const [view, setView] = useState<ViewMode>("timeline");
  const [events] = useLocalStorageState<CalendarEvent[]>("hackstage:events", INITIAL_EVENTS);
  const [posts, setPosts] = useLocalStorageState<TimelinePost[]>(
    "hackstage:posts",
    INITIAL_TIMELINE_POSTS
  );

  const scopedEvents = events.filter((e) => e.scope === scope);
  const scopedPosts = posts
    .filter((p) => p.scope === scope)
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  function handleReact(postId: string, kind: ReactionKind) {
    setPosts((prev) =>
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

  function handleNewPost(content: string) {
    const newPost: TimelinePost = {
      id: `p-${Date.now()}`,
      scope,
      author: "自分",
      content,
      createdAt: new Date().toISOString(),
      reactions: { fire: 0, thumbsUp: 0, muscle: 0, party: 0 },
      myReaction: null,
    };
    setPosts((prev) => [newPost, ...prev]);
  }

  return (
    <div className="space-y-4 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">タイムライン</h1>
        <p className="text-xs text-[var(--color-muted)]">
          仲間の進捗を確認して、今日やることを整えよう
        </p>
      </header>

      <ScopeTabs scope={scope} onChange={setScope} groupName={GROUP_INFO.name} />
      <UpcomingStrip events={scopedEvents} />
      <ViewToggle mode={view} onChange={setView} />

      {view === "calendar" ? (
        <MonthCalendar events={scopedEvents} />
      ) : (
        <div className="space-y-3">
          <NewPostBox onSubmit={handleNewPost} />
          {scopedPosts.length === 0 ? (
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
