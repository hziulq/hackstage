# nextstage 設計値

実装中に**引く**ための文書。原則と禁止事項は `.specify/memory/constitution.md`（憲章）にある。
本文書は憲章に従属する。矛盾する場合は憲章を正とし、本文書を修正する。

記載された境界・命名・キー名を変更する場合、**先に本文書を更新する**（憲章 原則 I）。

---

## 1. 技術スタック

| 領域 | 採用 |
|---|---|
| フロントエンド | Next.js (App Router) / TypeScript |
| バックエンド | Flask / Python 3.12 |
| DB | PostgreSQL（Render マネージド） |
| コンテナ | Docker（マルチステージ: `dev` / `prod`） |
| ホスティング | Render（Blueprint = `render.yaml` 管理） |
| ローカル開発 | Docker Compose + devcontainer |

---

## 2. サービス構成

```
                    ┌──────────────────────────────┐
  ブラウザ ────────> │ web (Next.js)  type: web      │  ← 公開。唯一の入口
                    │  /api/* を rewrites でプロキシ │
                    └──────────────┬───────────────┘
                                   │ internal network
                    ┌──────────────▼───────────────┐
                    │ api (Flask)   type: pserv     │  ← 非公開
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │ db (PostgreSQL)               │
                    └──────────────────────────────┘
```

---

## 3. ディレクトリ構成

各アプリを自己完結させ、Docker の Build Context をアプリ配下に閉じる（`rootDir` 方式）。
Next.js と Flask で言語が異なるため、共有コードのディレクトリは作らない。型共有は `openapi.json` 経由。

```
nextstage/
├── README.md                    # 起動手順のみ（規約値を再掲しない）
├── CONTRIBUTING.md              # ブランチ運用・PR 手順
├── render.yaml                  # Render 構成（本番）
├── compose.yaml                 # ローカル開発構成（dev / web / api / db）
├── .env.example                 # 環境変数のキー一覧（値は空。コミットする）
├── .gitignore
├── openapi.json                 # api が生成 → web が型生成に使用（コミットする）
│
├── docs/
│   └── design.md                # 本文書
│
├── .devcontainer/
│   ├── devcontainer.json        # compose.yaml を参照。service: dev
│   └── Dockerfile               # Node + Python 3.12 + psql + pwsh
│
├── .specify/                    # Spec Kit（共有資産）
│   └── memory/constitution.md   # 憲章
│
├── specs/                       # 仕様（任意。全機能を網羅しない）
│   └── NNN-slug/
│
├── apps/
│   ├── web/                     # ── フロントエンド担当の作業範囲
│   │   ├── Dockerfile           # target: dev / prod
│   │   ├── .dockerignore
│   │   ├── next.config.js       # rewrites 設定（§5）
│   │   ├── middleware.ts        # 画面ガード
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── src/
│   │       ├── app/
│   │       │   ├── (public)/    # 未ログインで見せる画面（/login 等）
│   │       │   └── (protected)/ # ログイン必須の画面
│   │       ├── components/
│   │       └── lib/
│   │           └── api.ts       # api 呼び出しラッパ（Cookie 転送を集約。§6）
│   │
│   └── api/                     # ── バックエンド担当の作業範囲
│       ├── Dockerfile           # target: dev / prod
│       ├── .dockerignore
│       ├── requirements.txt
│       ├── wsgi.py              # 本番エントリポイント（gunicorn が読む）
│       └── app/
│           ├── __init__.py      # create_app()（Application Factory）
│           ├── config.py        # 環境変数の読み込みを一元化
│           ├── extensions.py    # db, login_manager 等の初期化
│           ├── models/          # SQLAlchemy モデル
│           ├── schemas/         # 入力検証スキーマ
│           ├── auth/            # 認証・認可
│           └── routes/          # エンドポイント
│
└── migrations/                  # Alembic（api 担当が管理）
```

**ディレクトリ命名を変えないこと。** `render.yaml` の `rootDir`、`compose.yaml` の `context`、
`devcontainer.json` の `workspaceFolder` が上記パスに依存している。

---

## 4. ポートと起動方式

| | dev（compose / devcontainer） | prod（Render） |
|---|---|---|
| web | `next dev` / 3000 | `next start`（standalone） / `$PORT` |
| api | `flask run --debug` / 8000 | `gunicorn wsgi:app` / `$PORT` |

- 本番は `$PORT` から待ち受ける（憲章 原則 VII）。`api` はこの `$PORT` の値を `8000` に固定する（§9）。
- ローカルはソースを volume マウントしてホットリロードする。

---

## 5. 通信経路

`web` の `next.config.js` に rewrites を定義し、`/api/:path*` を `API_INTERNAL_URL` へ転送する。

```
ブラウザ → https://<web>/api/login → [rewrites] → http://api:8000/api/login
```

rewrites を実行するのは**ブラウザではなく `web` の Node プロセス**である。ブラウザは自分と同じ
オリジンを叩き、`web` → `api` はプライベートネットワーク内で完結する。したがってブラウザは
`api` のホスト名を一度も名前解決しない。

**`API_INTERNAL_URL` はローカルと本番で同じ値 `http://api:8000` を使う。**
compose のサービス名と Render のサービス名を両方 `api` に揃えているため、環境差分が発生しない。

- ホスト名 `api` はサービス名で解決される（compose の組み込み DNS / Render の内部 DNS）。
  `localhost` は「同じコンテナの内側」を指すため、`web` から `api` を呼ぶ用途では使えない。
- **`API_INTERNAL_URL` のポートは `api` が実際に待ち受けるポートと一致させる。**
  Render が注入する `$PORT` の既定値は 8000 ではないため、`render.yaml` の `api` に
  `PORT: 8000` を明示する。明示しないと本番のみ接続できない（ローカルでは再現しない）。
- Render 側の internal アドレスはダッシュボードの表示で最終確認する。

---

## 6. API の呼び出し方

**実行場所によって呼び方が異なる。** Client Component と Server Component で規約が違う。

| 呼び出し元 | 宛先 | Cookie |
|---|---|---|
| Client Component（ブラウザ） | 相対パス `/api/...` | ブラウザが自動送信。`credentials` は既定値のまま |
| Server Component / Server Action | `${API_INTERNAL_URL}/api/...`（絶対 URL） | **手動転送が必要**（`next/headers` の `cookies()`） |
| `middleware.ts` | 原則として `api` を呼ばない | Cookie の存在確認のみ |

```ts
// Client Component — 相対パス
'use client'
const res = await fetch('/api/posts', { method: 'POST', body: JSON.stringify(x) })

// Server Component — 絶対 URL + Cookie 手動転送
import { cookies } from 'next/headers'
const res = await fetch(`${process.env.API_INTERNAL_URL}/api/me`, {
  headers: { cookie: (await cookies()).toString() },
  cache: 'no-store',
})
```

- Server Component で相対パスの `fetch` はサーバ上にオリジンが無いため失敗する。
- 上記 2 経路の差分は `apps/web/src/lib/api.ts` に集約する。呼び出し側に分岐を散らさない。
- `apps/web` に `app/api/**/route.ts` を作らない（憲章 原則 II）。
  `rewrites()` が配列を返す形はファイルシステムのルートが優先されるため、プロキシを塞ぐ。
  `web` 自身が返すのは `/healthz` のみ（`/api/` の外）。

---

## 7. API 契約

| 項目 | 規約 |
|---|---|
| パス接頭辞 | すべて `/api/` 配下 |
| 形式 | JSON（リクエスト / レスポンスとも） |
| 認証エラー | 未ログイン → `401` / 権限なし → `404` |
| 入力エラー | `400` + `{"error": {"code": "...", "message": "...", "fields": {...}}}` |
| 成功時 | `200` / `201`。エンベロープで包まない（データを直接返す） |
| スキーマ | `api` が `openapi.json` を生成しリポジトリにコミット |
| 型共有 | `web` は `openapi.json` から TypeScript 型を生成する |

### 認証系エンドポイント

| メソッド | パス | 用途 |
|---|---|---|
| POST | `/api/login` | 認証してセッション Cookie を発行 |
| POST | `/api/logout` | セッション破棄 |
| GET | `/api/me` | 現在のユーザー情報。未ログインは 401 |
| GET | `/api/health` | ヘルスチェック（認証不要） |

---

## 8. 認証・認可の実装詳細

### 方式

**Flask のサーバーサイド署名付き Cookie セッション**（`flask_login` + Flask 標準 `session`）を採用する。
JWT は採用しない（憲章 原則 IV / 未決事項）。理由: 外部クライアント（モバイル等）の予定が
現時点で無く、失効管理のコストに見合わないため。将来 JWT へ移行する場合も Flask 内部の
差し替えのみで済む設計にする。

### 責務の境界

| 責務 | 担当 | 内容 |
|---|---|---|
| パスワード検証・ハッシュ | **api** | 方式は憲章 原則 IV |
| セッション発行 / 破棄 | **api** | `POST /api/login` / `POST /api/logout` |
| **API の認証・認可判定** | **api（必須）** | ここが唯一のセキュリティ境界 |
| 画面遷移の制御 | **web** | `middleware.ts` |
| ボタン・メニューの表示制御 | **web** | UX のみ。防御ではない |
| ログイン画面の UI | **web** | |

### Cookie 属性

| 属性 | 値 |
|---|---|
| `HttpOnly` | 常に true |
| `Secure` | 本番 true / ローカル false（`SESSION_COOKIE_SECURE` で分岐。ローカルは HTTP のため） |
| `SameSite` | `Lax` |
| `Path` | `/` |
| 有効期限 | 7 日（`PERMANENT_SESSION_LIFETIME`） |

### ユーザー情報の表示

HttpOnly Cookie は Client Component から読めない。したがって:

- ユーザー名等の表示は Server Component から `GET /api/me` を呼んで取得する
- Client Component へは props で渡す

### レート制限

`POST /api/login` に Flask-Limiter でレート制限をかける。

---

## 9. 環境変数

キー名は**この表のとおりに実装する**。`.env.example` にも同じキーを列挙する。

| キー | 対象 | ローカル（`.env`） | 本番（Render） | 機密 |
|---|---|---|---|---|
| `API_INTERNAL_URL` | web | `http://api:8000` | `http://api:8000` | – |
| `NODE_ENV` | web | `development` | `production` | – |
| `PORT` | web | – | Render が自動注入（値に依存しない） | – |
| `PORT` | api | – | **`8000` を明示**（`API_INTERNAL_URL` と一致させる） | – |
| `FLASK_ENV` | api | `development` | `production` | – |
| `SECRET_KEY` | api | 任意のローカル値 | **`sync: false`**（手入力） | ✅ |
| `DATABASE_URL` | api / dev | `postgresql://...@db:5432/nextstage` | `fromDatabase`（自動） | ✅ |
| `SESSION_COOKIE_SECURE` | api | `false` | `true` | – |

- `dev` サービスは `api` と同じ `.env` を読む。開発用に別のキーを新設しない。
- キーを追加するときの手順は `CONTRIBUTING.md` §3 にある。

---

## 10. 開発環境（devcontainer）

`compose.yaml` は 4 サービスを定義する: `dev` / `web` / `api` / `db`。

| サービス | 役割 |
|---|---|
| `dev` | devcontainer のアタッチ先。Node + Python 3.12 + psql + pwsh を持つ作業用コンテナ。`command: sleep infinity` |
| `web` | `next dev`（ホットリロード） |
| `api` | `flask run --debug`（ホットリロード） |
| `db` | PostgreSQL |

`devcontainer.json` の設定:

```jsonc
{
  "dockerComposeFile": "../compose.yaml",
  "service": "dev",
  "runServices": ["dev", "web", "api", "db"],
  "workspaceFolder": "/workspaces/nextstage",
  "features": {
    "ghcr.io/devcontainers/features/powershell:1": {}
  }
}
```

- **アタッチ先を `web` にしないこと。** `web` の image は Node のみで Python を持たないため、
  api 担当が同じ環境を使えない。両方の言語を持つ `dev` を唯一のアタッチ先とする。
- アプリのプロセスは `web` / `api` コンテナ側で動かす。`dev` は編集・型生成・Alembic 実行・
  `psql`・git・Spec Kit コマンドの実行場所とする。
- `dev` は `db:5432` に到達できること（Alembic を `dev` から実行するため）。
- **`pwsh` が必要。** Spec Kit は `.specify/scripts/powershell/*.ps1` のみを提供しており、
  10 コマンドのうち 8 つがこれを実行する（`specify` と `constitution` 以外）。
- **`dev` サービスを `render.yaml` に含めないこと。** 本番に存在しない。
- `.devcontainer/Dockerfile` は開発専用。`apps/*/Dockerfile` を流用しない。

---

## 11. Render 設定値

### web

| 項目 | 値 |
|---|---|
| `type` | `web` |
| `runtime` | `docker` |
| `rootDir` | `apps/web` |
| `dockerfilePath` | `./Dockerfile` |
| `dockerContext` | `.` |
| `dockerTarget` | `prod` |
| `healthCheckPath` | `/healthz`（Next.js 自身が返す。`/api/*` を使わない） |
| `buildFilter.paths` | `apps/web/**`, `openapi.json` |

### api

| 項目 | 値 |
|---|---|
| `type` | `pserv` |
| `runtime` | `docker` |
| `rootDir` | `apps/api` |
| `dockerfilePath` | `./Dockerfile` |
| `dockerContext` | `.` |
| `dockerTarget` | `prod` |
| `envVars` | `PORT: 8000` を明示、`SECRET_KEY` は `sync: false` |
| `buildFilter.paths` | `apps/api/**` |

### db

| 項目 | 値 |
|---|---|
| `databases[].name` | `db` |
| 接続 | `api` の `DATABASE_URL` に `fromDatabase` で注入 |

### 共通

- `previews: generation: automatic`（PR ごとに web + api + db を一式複製）
- `buildFilter` は**必須**。省略すると push ごとに全サービスが再ビルドされる
- `render.yaml` に `dev` サービスを含めない

---

## 12. ローカルと本番の対応

| | ローカル | 本番 |
|---|---|---|
| 構成定義 | `compose.yaml` | `render.yaml` |
| 開発環境 | `.devcontainer/`（`dev` サービス） | 該当なし |
| Dockerfile | 同一（`target: dev`） | 同一（`dockerTarget: prod`） |
| DB | compose の `db` コンテナ | Render マネージド Postgres |
| 環境変数 | `.env` | ダッシュボード / `envVars` |
| api への到達 | `http://api:8000` | `http://api:8000`（internal） |

**`compose.yaml` と `render.yaml` は自動同期しない。**
差分の発生を抑えるため、ポート・起動コマンド・依存インストールは
**YAML ではなく Dockerfile 側に寄せる**。

---

## 13. 担当分担と成果物

| 担当 | 作成物 |
|---|---|
| **インフラ** | `render.yaml`, `compose.yaml`, `.devcontainer/**`, 両 `Dockerfile`, `.dockerignore`, `.env.example`, `.gitignore`, `README.md` |
| **バックエンド（api）** | `apps/api/**`, `migrations/**`, `openapi.json` の生成 |
| **フロントエンド（web）** | `apps/web/**`（`next.config.js` の rewrites, `middleware.ts` を含む） |

担当範囲を越えたファイル変更は行わない。必要な場合は担当者に依頼するか、PR で明示的に合意する。

### 担当間のインターフェース（先に固定済み）

以下が決まっているため、3 担当は並行して着手できる。

1. `api` は `/api/*` で JSON を返す（§7）
2. 認証は Cookie。`web` は Cookie を透過させるだけでよい（§8）
3. `web` → `api` は `API_INTERNAL_URL` 経由（§5）
4. 環境変数キー名は §9 で固定
