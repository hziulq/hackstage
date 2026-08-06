# Quickstart: 掲示板・目標・カレンダーAPI認証統合の動作確認

`apps/api/README.md`の運用に従い、確認は**`dev`コンテナ内**から`http://api:8000`に対して行う
(憲章 原則VI)。

## 前提: 依存関係とopenapi.jsonの反映

```bash
# dev コンテナ内
pip install --user -r apps/api/requirements.txt
cd apps/api && python generate_openapi.py && cd ../..

# apps/web側の型再生成
cd apps/web && npm run generate:api-types && cd ../..
```

```bash
# ホスト側ターミナル(dev コンテナには Docker CLI が無いため)
docker compose build api
docker compose up -d api
```

## シナリオ1: 未ログインは401(SC-001, FR-001)

```bash
curl -s -i -X POST http://api:8000/api/goals \
  -H 'Content-Type: application/json' \
  -d '{"company_name":"テスト株式会社","stage":"ES","target_date":"2026-12-01"}'

curl -s -i -X POST http://api:8000/api/posts \
  -H 'Content-Type: application/json' \
  -d '{"category":"anonymous_qa","body":"質問です"}'

curl -s -i -X POST http://api:8000/api/reactions \
  -H 'Content-Type: application/json' \
  -d '{"target_type":"post","target_id":1,"kind":"fire"}'
```

**期待結果**: いずれも`401 {"error":{"code":"unauthorized",...}}`、データは作成されない。

## シナリオ2: 他人の`user_id`を指定しても本人としてしか操作できない(SC-002, FR-002)

```bash
COOKIE_A=$(mktemp)
COOKIE_B=$(mktemp)

# ユーザーA・Bをそれぞれ登録・ログイン
curl -s -X POST http://api:8000/api/register -H 'Content-Type: application/json' \
  -d '{"email":"user-a@example.com","password":"correct-horse","display_name":"ユーザーA"}'
curl -s -c "$COOKIE_A" -X POST http://api:8000/api/login -H 'Content-Type: application/json' \
  -d '{"email":"user-a@example.com","password":"correct-horse"}'

curl -s -X POST http://api:8000/api/register -H 'Content-Type: application/json' \
  -d '{"email":"user-b@example.com","password":"correct-horse","display_name":"ユーザーB"}'
curl -s -c "$COOKIE_B" -X POST http://api:8000/api/login -H 'Content-Type: application/json' \
  -d '{"email":"user-b@example.com","password":"correct-horse"}'

# ユーザーAとしてuser_idにユーザーBのidを指定して目標を作成 → user_idは無視され current_user(A)のものになる
curl -s -i -b "$COOKIE_A" -X POST http://api:8000/api/goals \
  -H 'Content-Type: application/json' \
  -d '{"user_id":9999,"company_name":"なりすまし企業","stage":"ES","target_date":"2026-12-01"}'
# → レスポンスのuser_idがユーザーA自身のidになっていることを確認

# ユーザーBがユーザーAの目標を削除しようとする → 404
GOAL_ID=<上記レスポンスのid>
curl -s -i -b "$COOKIE_B" -X DELETE "http://api:8000/api/goals/$GOAL_ID"
```

**期待結果**: 作成時は`user_id`指定に関わらず`current_user`(ユーザーA)のものとして作成される。
ユーザーBからの削除は`404 {"error":{"code":"not_found",...}}`で拒否される。

## シナリオ3: カレンダー参加者本人以外は404(spec.md Edge Cases)

```bash
# ユーザーBが、参加していないカレンダー(例: id=1、ユーザーAのグループ)を取得しようとする
curl -s -i -b "$COOKIE_B" http://api:8000/api/calendars/1
curl -s -i -b "$COOKIE_B" http://api:8000/api/calendars/1/members

# 未ログインでの取得 → 401
curl -s -i http://api:8000/api/calendars/1
```

**期待結果**: 非参加者は`404`(`403`ではない)、未ログインは`401`。

## シナリオ4: `openapi.json`と生成型の一致(SC-004, FR-005, FR-006)

```bash
cd apps/api
python generate_openapi.py
git diff --stat ../../openapi.json   # 再実行しても差分が出ないこと(再現性)
python -c "
import json
spec = json.load(open('../../openapi.json'))
paths = sorted(spec['paths'].keys())
print(paths)
assert '/api/posts' in paths and '/api/goals' in paths and '/api/events' in paths
assert '/api/reactions' in paths and '/api/calendars/{calendar_id}' in paths
"
cd ../web
npm run generate:api-types
git diff --stat src/lib/api-types.generated.ts
```

**期待結果**: `openapi.json`に新規パスが含まれ、再実行で差分が出ない。
`api-types.generated.ts`が更新され、既存のregister/login/logout/me/todos型のフィールドは
変わらない(diffで確認)。

## シナリオ5: ブラウザでの登録・ログイン・認証必須ページ(SC-003, FR-004)

```bash
# ホスト側 or devcontainerのポートフォワード経由で apps/web (next dev) にアクセス
```

1. 未ログイン状態で `/timeline`・`/goals`・`/board`・`/mypage` のいずれかを開く →
   `/login?next=...` にリダイレクトされることを確認。
2. `/register` で新規登録 → `/login`に案内される(自動ログインしない)ことを確認。
3. `/login` でログイン → `/timeline` に遷移し、Cookieがセットされることを確認
   (ブラウザの開発者ツールでHttpOnly Cookie `session` の存在を確認)。
4. ログイン済み状態で `/login`・`/register` を開く → `/timeline` にリダイレクトされることを確認
   (`proxy.ts`のAUTH_ONLY_PATHSの挙動)。

**注記**: `next build`(本番ビルド)の成否確認はこのdevcontainer(Docker Desktop for Windows + WSL2)
では既知の環境固有問題により信頼できない。ビルド成否はホストOSまたはGitHub Actions CI
(`web-ci.yml`)で確認する。`next dev`でのブラウザ確認はdevcontainer内で問題なく行える。

## 詳細な契約

各エンドポイントのリクエスト/レスポンス形式・認可ルールは
[contracts/social-api.md](./contracts/social-api.md)を参照。
