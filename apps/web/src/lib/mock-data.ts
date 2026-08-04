import type {
  BoardPost,
  CalendarEvent,
  GroupInfo,
  InternshipInfo,
  Member,
  TimelinePost,
} from "./types";
import { generateMilestones } from "./milestones";
import type { Goal } from "./types";

function shiftDate(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

export const GROUP_INFO: GroupInfo = {
  name: "ジュラシック・パーク",
  inviteCode: "DINO-2027",
};

export const INITIAL_EVENTS: CalendarEvent[] = [
  { id: "e1", scope: "group", title: "合同企業説明会", date: shiftDate(1), time: "13:00", location: "オンライン" },
  { id: "e2", scope: "group", title: "グループES締切", date: shiftDate(3), time: "23:59" },
  { id: "e3", scope: "personal", title: "Webテスト対策", date: shiftDate(2), time: "20:00" },
  { id: "e4", scope: "group", title: "OB訪問（先輩と）", date: shiftDate(6), time: "18:30", location: "渋谷" },
  { id: "e5", scope: "personal", title: "面接練習（模擬面接）", date: shiftDate(9), time: "10:00" },
  { id: "e6", scope: "group", title: "インターン説明会", date: shiftDate(14), time: "15:00", location: "オンライン" },
];

export const INITIAL_TIMELINE_POSTS: TimelinePost[] = [
  {
    id: "p1",
    scope: "group",
    author: "れっくす",
    content: "今日のWebテスト対策、模擬問題を3周やった！みんなも頑張ろう🔥",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    reactions: { fire: 4, thumbsUp: 2, muscle: 1, party: 0 },
    myReaction: null,
  },
  {
    id: "p2",
    scope: "group",
    author: "とりけら",
    content: "一次面接通過しました！次は二次面接、対策アドバイスあれば教えてください🙏",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
    reactions: { fire: 1, thumbsUp: 6, muscle: 3, party: 8 },
    myReaction: "party",
  },
  {
    id: "p3",
    scope: "personal",
    author: "自分",
    content: "ES下書き終わった。あとは添削出す。",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 30).toISOString(),
    reactions: { fire: 0, thumbsUp: 1, muscle: 0, party: 0 },
    myReaction: null,
  },
];

export const INITIAL_GOALS: Goal[] = [
  {
    id: "g1",
    companyName: "株式会社ダイノテック",
    stage: "二次面接",
    targetDate: shiftDate(21),
    createdAt: new Date().toISOString(),
    milestones: generateMilestones(shiftDate(21)).map((m, i) => ({ ...m, done: i < 2 })),
  },
];

export const INITIAL_BOARD_POSTS: BoardPost[] = [
  {
    id: "b1",
    title: "Webテストの電卓は使っていい？",
    body: "玉手箱形式の企業を受けるのですが、電卓の使用ルールがよくわかりません。企業ごとに違いますか？",
    tags: ["Webテスト", "選考"],
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    answers: [
      { id: "a1", body: "企業ごとに違います。募集要項か受検案内メールに書いてあることが多いです。", createdAt: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString() },
    ],
  },
  {
    id: "b2",
    title: "ガクチカ、複数エピソード使い回してもいい？",
    body: "サークルとアルバイトの2つのエピソードを企業によって使い分けようと思っていますが、印象悪いでしょうか。",
    tags: ["ES", "ガクチカ"],
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(),
    answers: [],
  },
  {
    id: "b3",
    title: "オンライン面接、カメラの高さどうしてる？",
    body: "画角が不自然になりがちで悩んでいます。みんなの工夫を教えてください。",
    tags: ["面接", "オンライン"],
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 50).toISOString(),
    answers: [
      { id: "a2", body: "本を積んでノートPCの下に置いて目線の高さに調整してます。", createdAt: new Date(Date.now() - 1000 * 60 * 60 * 40).toISOString() },
      { id: "a3", body: "外部Webカメラを目線の高さに三脚で固定するのがおすすめです。", createdAt: new Date(Date.now() - 1000 * 60 * 60 * 30).toISOString() },
    ],
  },
];

export const ALL_BOARD_TAGS = Array.from(
  new Set(INITIAL_BOARD_POSTS.flatMap((p) => p.tags))
);

export const INITIAL_MEMBERS: Member[] = [
  { id: "m1", name: "とりけら", score: 980, avatarColor: "#f97316" },
  { id: "m2", name: "れっくす", score: 860, avatarColor: "#ef4444" },
  { id: "m3", name: "ぷてらの", score: 720, avatarColor: "#8b5cf6" },
  { id: "m4", name: "自分", score: 640, avatarColor: "#5b5fee" },
  { id: "m5", name: "すてご", score: 510, avatarColor: "#22c55e" },
];

export const INTERNSHIP_INFO: InternshipInfo[] = [
  { id: "i1", region: "関東", company: "株式会社ダイノテック", title: "冬季1day仕事体験", period: "2026-12", tags: ["IT", "1day"] },
  { id: "i2", region: "関東", company: "ラプター商事", title: "3日間ビジネス実践インターン", period: "2027-01", tags: ["商社", "3日間"] },
  { id: "i3", region: "関西", company: "トリケラ製薬", title: "研究職体験インターン", period: "2026-12", tags: ["メーカー", "研究"] },
  { id: "i4", region: "中部", company: "ステゴサウルス工業", title: "ものづくり現場体感コース", period: "2027-02", tags: ["メーカー", "1day"] },
  { id: "i5", region: "九州", company: "プテラノ銀行", title: "長期実践型インターン", period: "2026-09〜", tags: ["金融", "長期"] },
];

export const REGIONS = ["すべて", "関東", "関西", "中部", "九州"] as const;
