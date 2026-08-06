# API Contract: グループカレンダー作成・参加・予定作成

`docs/design.md` §7の規約(パス接頭辞`/api/`、JSON、成功時はエンベロープなし、
入力エラーは`400 {"error": {"code","message","fields"}}`、未ログインは`401`、
**権限なしは`404`固定**(`403`は使わない、憲章 原則III))に従う。

## POST /api/calendars

グループカレンダーの新規作成(FR-001, FR-002)。

**Request**
```json
{ "name": "同期就活グループ" }
```

**Response — 成功**: `201 Created`(作成者は自動的に`role="owner"`の参加者になる)
```json
{ "id": 12, "name": "同期就活グループ", "type": "group", "owner_id": 5, "invite_code": "aB3dEfGh" }
```

**Response — バリデーションエラー**: `400 Bad Request`
```json
{ "error": { "code": "invalid_request", "message": "validation failed", "fields": { "name": ["Length must be between 1 and 100."] } } }
```

**Response — 未ログイン**: `401 Unauthorized`

## POST /api/calendars/join

招待コードでの既存グループへの参加(FR-003, FR-004, FR-005)。

**Request**
```json
{ "invite_code": "aB3dEfGh" }
```

**Response — 新規参加**: `201 Created`
```json
{ "id": 12, "name": "同期就活グループ", "type": "group", "owner_id": 5, "invite_code": "aB3dEfGh" }
```

**Response — 既に参加済み(冪等、FR-005)**: `200 OK`(ボディは上記と同形式)

**Response — 無効な招待コード**: `404 Not Found`
```json
{ "error": { "code": "not_found", "message": "招待コードが見つかりません。" } }
```

**Response — 未ログイン**: `401 Unauthorized`

## POST /api/events

予定の作成(FR-006, FR-007)。

**Request**
```json
{
  "calendar_id": 12,
  "category": "interview",
  "title": "一次面接",
  "start_at": "2026-09-01T10:00:00+09:00",
  "is_private": false
}
```

**Response — 成功**: `201 Created`(`user_id`はクライアント指定不可、`current_user.id`で作成)
```json
{
  "id": 30, "calendar_id": 12, "user_id": 5, "category": "interview",
  "title": "一次面接", "start_at": "2026-09-01T01:00:00+00:00", "end_at": null,
  "is_all_day": false, "location": null, "memo": null, "is_private": false,
  "created_at": "2026-08-06T00:00:00+00:00", "updated_at": "2026-08-06T00:00:00+00:00"
}
```

**Response — バリデーションエラー**: `400 Bad Request`

**Response — 参加していないカレンダー**: `404 Not Found`(既存の`GET /api/events`と同じ判定)

**Response — 未ログイン**: `401 Unauthorized`

## 既存エンドポイントとの関係(変更なし)

- `GET /api/calendars/{calendar_id}` / `GET /api/calendars/{calendar_id}/members`: 本feature後、
  グループカレンダーに対しても参加者であれば同様に取得できる(`010`から実装変更なし)。
- `GET /api/events?calendar_id=...`: 本feature後に作成した予定も、既存の`is_private`フィルタに
  従って一覧に反映される(実装変更なし)。

## 共通の副作用

- 上記3エンドポイントに`security: - cookieAuth: []`を`generate_openapi.py`が拾えるdocstringで
  明記し、`openapi.json`に反映する。
- `apps/web/src/lib/api-types.generated.ts`を`npm run generate:api-types`で再生成する。
