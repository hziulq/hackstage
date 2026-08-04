"use client";

import { useMemo, useState } from "react";
import { useLocalStorageState } from "@/hooks/useLocalStorageState";
import { INITIAL_BOARD_POSTS } from "@/lib/mock-data";
import type { BoardPost } from "@/lib/types";
import TagFilter from "@/components/board/TagFilter";
import QuestionCard from "@/components/board/QuestionCard";
import NewQuestionForm from "@/components/board/NewQuestionForm";

export default function BoardPage() {
  const [posts, setPosts] = useLocalStorageState<BoardPost[]>(
    "hackstage:board",
    INITIAL_BOARD_POSTS
  );
  const [activeTag, setActiveTag] = useState<string | null>(null);

  const allTags = useMemo(
    () => Array.from(new Set(posts.flatMap((p) => p.tags))),
    [posts]
  );

  const filtered = useMemo(() => {
    const list = activeTag ? posts.filter((p) => p.tags.includes(activeTag)) : posts;
    return [...list].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }, [posts, activeTag]);

  function handleCreate(input: { title: string; body: string; tags: string[] }) {
    const newPost: BoardPost = {
      id: `b-${Date.now()}`,
      title: input.title,
      body: input.body,
      tags: input.tags,
      createdAt: new Date().toISOString(),
      answers: [],
    };
    setPosts((prev) => [newPost, ...prev]);
  }

  function handleAddAnswer(postId: string, body: string) {
    setPosts((prev) =>
      prev.map((p) =>
        p.id !== postId
          ? p
          : {
              ...p,
              answers: [
                ...p.answers,
                { id: `a-${Date.now()}`, body, createdAt: new Date().toISOString() },
              ],
            }
      )
    );
  }

  return (
    <div className="space-y-4 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">匿名掲示板</h1>
        <p className="text-xs text-[var(--color-muted)]">
          誰が聞いたか気にせず、選考の疑問をQ&amp;Aで解決しよう
        </p>
      </header>

      {allTags.length > 0 && (
        <TagFilter tags={allTags} active={activeTag} onChange={setActiveTag} />
      )}

      <NewQuestionForm onCreate={handleCreate} />

      {filtered.length === 0 ? (
        <p className="py-8 text-center text-sm text-[var(--color-muted)]">
          該当する質問がありません
        </p>
      ) : (
        <div className="space-y-3">
          {filtered.map((post) => (
            <QuestionCard key={post.id} post={post} onAddAnswer={handleAddAnswer} />
          ))}
        </div>
      )}
    </div>
  );
}
