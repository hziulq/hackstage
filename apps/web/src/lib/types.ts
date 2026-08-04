export type ReactionKind = "fire" | "thumbsUp" | "muscle" | "party";

export const REACTIONS: { kind: ReactionKind; emoji: string; label: string }[] = [
  { kind: "fire", emoji: "🔥", label: "熱い" },
  { kind: "thumbsUp", emoji: "👍", label: "いいね" },
  { kind: "muscle", emoji: "💪", label: "頑張れ" },
  { kind: "party", emoji: "🎉", label: "おめでとう" },
];

export interface CalendarEvent {
  id: string;
  scope: "group" | "personal";
  title: string;
  date: string; // YYYY-MM-DD
  time?: string; // HH:mm
  location?: string;
}

export interface TimelinePost {
  id: string;
  scope: "group" | "personal";
  author: string;
  content: string;
  createdAt: string; // ISO
  reactions: Record<ReactionKind, number>;
  myReaction: ReactionKind | null;
}

export type MilestoneStatus = "done" | "overdue" | "today" | "upcoming";

export interface Milestone {
  id: string;
  title: string;
  dueDate: string; // YYYY-MM-DD
  offsetDays: number; // 目標日からの日数（正=前）
  done: boolean;
}

export interface Goal {
  id: string;
  companyName: string;
  stage: string;
  targetDate: string; // YYYY-MM-DD
  createdAt: string;
  milestones: Milestone[];
}

export interface BoardAnswer {
  id: string;
  body: string;
  createdAt: string;
}

export interface BoardPost {
  id: string;
  title: string;
  body: string;
  tags: string[];
  createdAt: string;
  answers: BoardAnswer[];
}

export interface Member {
  id: string;
  name: string;
  score: number;
  avatarColor: string;
}

export interface InternshipInfo {
  id: string;
  region: string;
  company: string;
  title: string;
  period: string;
  tags: string[];
}

export interface GroupInfo {
  name: string;
  inviteCode: string;
}
