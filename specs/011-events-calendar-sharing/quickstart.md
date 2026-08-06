# Quickstart: グループカレンダーの作成・共有と予定作成の動作確認

`apps/api/README.md`の運用に従い、確認は**`dev`コンテナ内**から`http://api:8000`に対して行う
(憲章 原則VI)。

## 前提: openapi.jsonと型の反映

```bash
cd apps/api && python generate_openapi.py && cd ../..
cd apps/web && npm run generate:api-types && cd ../..
```

## シナリオ1: グループ作成→招待コード発行(SC-001, FR-001, FR-002)

```bash
COOKIE_A=$(mktemp)
curl -s -c "$COOKIE_A" -X POST http://api:8000/api/login -H 'Content-Type: application/json' \
  -d '{"email":"user-a@example.com","password":"correct-horse"}'

curl -s -i -b "$COOKIE_A" -X POST http://api:8000/api/calendars \
  -H 'Content-Type: application/json' -d '{"name":"同期就活グループ"}'
```

**期待結果**: `201`、レスポンスに`invite_code`が含まれる。`GET /api/calendars/{id}/members`で
作成者自身が`role=owner`として表示される。

## シナリオ2: 招待コードでの参加(SC-002, FR-003, FR-004, FR-005)

```bash
COOKIE_B=$(mktemp)
curl -s -c "$COOKIE_B" -X POST http://api:8000/api/login -H 'Content-Type: application/json' \
  -d '{"email":"user-b@example.com","password":"correct-horse"}'

INVITE_CODE=<シナリオ1のレスポンスのinvite_code>
curl -s -i -b "$COOKIE_B" -X POST http://api:8000/api/calendars/join \
  -H 'Content-Type: application/json' -d "{\"invite_code\":\"$INVITE_CODE\"}"

# 無効なコード
curl -s -i -b "$COOKIE_B" -X POST http://api:8000/api/calendars/join \
  -H 'Content-Type: application/json' -d '{"invite_code":"invalid-code"}'

# 重複参加(冪等であること)
curl -s -i -b "$COOKIE_B" -X POST http://api:8000/api/calendars/join \
  -H 'Content-Type: application/json' -d "{\"invite_code\":\"$INVITE_CODE\"}"
```

**期待結果**: 1回目は`201`、無効なコードは`404`、2回目の同じコードでの参加は`200`(エラーになら
ない)。参加後は`GET /api/calendars/{id}/members`にユーザーBも表示される。

## シナリオ3: 予定の作成と非公開設定(SC-003, SC-004, FR-006, FR-007)

```bash
CALENDAR_ID=<シナリオ1のレスポンスのid>

# ユーザーAが公開の予定を作成
curl -s -i -b "$COOKIE_A" -X POST http://api:8000/api/events \
  -H 'Content-Type: application/json' \
  -d "{\"calendar_id\":$CALENDAR_ID,\"category\":\"interview\",\"title\":\"一次面接\",\"start_at\":\"2026-09-01T10:00:00+09:00\"}"

# ユーザーAが非公開の予定を作成
curl -s -i -b "$COOKIE_A" -X POST http://api:8000/api/events \
  -H 'Content-Type: application/json' \
  -d "{\"calendar_id\":$CALENDAR_ID,\"category\":\"other\",\"title\":\"個人的な予定\",\"start_at\":\"2026-09-02T10:00:00+09:00\",\"is_private\":true}"

# ユーザーBの一覧(非公開の予定が見えないこと)
curl -s -b "$COOKIE_B" "http://api:8000/api/events?calendar_id=$CALENDAR_ID"

# 参加していないカレンダーへの作成(404になること)
COOKIE_C=$(mktemp)
curl -s -c "$COOKIE_C" -X POST http://api:8000/api/login -H 'Content-Type: application/json' \
  -d '{"email":"user-c@example.com","password":"correct-horse"}'
curl -s -i -b "$COOKIE_C" -X POST http://api:8000/api/events \
  -H 'Content-Type: application/json' \
  -d "{\"calendar_id\":$CALENDAR_ID,\"category\":\"other\",\"title\":\"侵入テスト\",\"start_at\":\"2026-09-03T10:00:00+09:00\"}"
```

**期待結果**: 公開・非公開ともに作成は`201`。ユーザーBの一覧には公開の予定のみ含まれる。
参加していないユーザーCからの作成は`404`。

## シナリオ4: openapi.json・生成型の一致(FR-009)

```bash
cd apps/api
python generate_openapi.py
git diff --stat ../../openapi.json   # 再実行しても差分が出ないこと
python -c "
import json
spec = json.load(open('../../openapi.json'))
paths = sorted(spec['paths'].keys())
assert '/api/calendars' in paths
assert '/api/calendars/join' in paths
print('OK')
"
```

## シナリオ5: ブラウザでのグループ作成・参加・予定作成(SC-005, FR-010)

1. ユーザーAでログインし、`/mypage`で「グループを作成」から新規グループを作成 → 招待コードが
   画面に表示されることを確認。
2. 別ブラウザ(またはシークレットウィンドウ)でユーザーBとしてログインし、`/mypage`で招待コードを
   入力して参加 → メンバーランキングにユーザーBが表示されることを確認。
3. ユーザーAが`/timeline`の「グループ」タブで予定を作成 → ユーザーBの`/timeline`にも同じ予定が
   表示されることを確認。

**注記**: `next build`の成否確認はこのdevcontainer環境では対象外(既知の環境固有問題、
`010-secure-social-api`の記録を参照)。`next dev`でのブラウザ確認は問題なく行える。

## 詳細な契約

各エンドポイントのリクエスト/レスポンス形式は
[contracts/calendars-events-api.md](./contracts/calendars-events-api.md)を参照。
