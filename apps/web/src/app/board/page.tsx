"use client";

import { useEffect, useMemo, useState } from "react";
import { postsClient, type ApiPost, type ApiPostComment } from "@/lib/posts";
import { ApiError } from "@/lib/api";
import type { BoardPost } from "@/lib/types";
import TagFilter from "@/components/board/TagFilter";
import QuestionCard from "@/components/board/QuestionCard";
import NewQuestionForm from "@/components/board/NewQuestionForm";

function toBoardPost(post: ApiPost, comments: ApiPostComment[]): BoardPost {
  return {
    id: String(post.id),
    title: post.title ?? "",
    body: post.body,
    tags: post.tags ?? [],
    createdAt: post.created_at ?? new Date().toISOString(),
    answers: comments.map((c) => ({
      id: String(c.id),
      body: c.body,
      createdAt: c.created_at ?? new Date().toISOString(),
    })),
  };
}

export default function BoardPage() {
  const [posts, setPosts] = useState<BoardPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTag, setActiveTag] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const apiPosts = await postsClient.list({ category: "anonymous_qa" });
        const withComments = await Promise.all(
          apiPosts.map(async (p) => toBoardPost(p, await postsClient.listComments(p.id!)))
        );
        if (!cancelled) setPosts(withComments);
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "読み込みに失敗しました");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const allTags = useMemo(
    () => Array.from(new Set(posts.flatMap((p) => p.tags))),
    [posts]
  );

  const filtered = useMemo(() => {
    const list = activeTag ? posts.filter((p) => p.tags.includes(activeTag)) : posts;
    return [...list].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }, [posts, activeTag]);

  async function handleCreate(input: { title: string; body: string; tags: string[] }) {
    try {
      const created = await postsClient.create({
        category: "anonymous_qa",
        title: input.title,
        body: input.body,
        tags: input.tags,
      });
      setPosts((prev) => [toBoardPost(created, []), ...prev]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "投稿に失敗しました");
    }
  }

  async function handleAddAnswer(postId: string, body: string) {
    try {
      const comment = await postsClient.addComment(Number(postId), body);
      setPosts((prev) =>
        prev.map((p) =>
          p.id !== postId
            ? p
            : {
                ...p,
                answers: [
                  ...p.answers,
                  { id: String(comment.id), body: comment.body, createdAt: comment.created_at ?? new Date().toISOString() },
                ],
              }
        )
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "回答の送信に失敗しました");
    }
  }

  return (
    <div className="space-y-4 px-4 pt-5">
      <header>
        <h1 className="text-lg font-bold">匿名掲示板</h1>
        <p className="text-xs text-[var(--color-muted)]">
          誰が聞いたか気にせず、選考の疑問をQ&amp;Aで解決しよう
        </p>
      </header>

      {error && <p className="text-xs text-red-500">{error}</p>}

      {allTags.length > 0 && (
        <TagFilter tags={allTags} active={activeTag} onChange={setActiveTag} />
      )}

      <NewQuestionForm onCreate={handleCreate} />

      {loading ? (
        <p className="py-8 text-center text-sm text-[var(--color-muted)]">読み込み中...</p>
      ) : filtered.length === 0 ? (
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
