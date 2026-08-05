# API Contract: 認証系エンドポイント

`docs/design.md` §7 の規約（パス接頭辞 `/api/`、JSON、成功時はエンベロープなし、入力エラーは `400 {"error": {"code","message","fields"}}`）に従う。

## POST /api/register

新規アカウント作成（オープン登録、FR-001）。

**Request**
```json
{ "email": "student@example.com", "password": "at-least-8-chars", "display_name": "山田太郎" }
```

**Response — 成功**: `201 Created`
```json
{ "id": 1, "email": "student@example.com", "display_name": "山田太郎", "avatar_url": null }
```

**Response — メール重複(FR-002)**: `400 Bad Request`
```json
{ "error": { "code": "invalid_request", "message": "email is already registered" } }
```

**Response — バリデーションエラー**: `400 Bad Request`
```json
{ "error": { "code": "invalid_request", "message": "validation failed", "fields": { "email": ["Not a valid email address."] } } }
```

## POST /api/login

メール・パスワードで認証しセッションCookieを発行(FR-003, FR-004)。

**Request**
```json
{ "email": "student@example.com", "password": "at-least-8-chars" }
```

**Response — 成功**: `200 OK`（`Set-Cookie` でセッション発行。属性は `docs/design.md` §8のCookie属性表に従う）
```json
{ "id": 1, "email": "student@example.com", "display_name": "山田太郎", "avatar_url": null }
```

**Response — 認証失敗（メール不存在・パスワード誤り区別なし、FR-008）**: `401 Unauthorized`
```json
{ "error": { "code": "invalid_credentials", "message": "email or password is incorrect" } }
```

**Response — レート制限超過(FR-009)**: `429 Too Many Requests`（Flask-Limiter既定のレスポンス形式）

## POST /api/logout

セッション破棄(FR-005)。ログイン必須。

**Response — 成功**: `204 No Content`

**Response — 未ログイン**: `401 Unauthorized`
```json
{ "error": { "code": "unauthorized", "message": "login required" } }
```

## GET /api/me

自分自身の基本情報取得(FR-006)。ログイン必須。

**Response — 成功**: `200 OK`
```json
{ "id": 1, "email": "student@example.com", "display_name": "山田太郎", "avatar_url": null }
```

**Response — 未ログイン(FR-007)**: `401 Unauthorized`
```json
{ "error": { "code": "unauthorized", "message": "login required" } }
```

## 副作用: 既存 `/api/todos/*` の認証必須化

本feature実装後、`GET/POST/PUT/DELETE /api/todos*` は全て `@login_required` になり、`user_id` はクエリパラメータではなく認証済みセッションの `current_user.id` から決まる。未ログインでのアクセスは `401`（従来の「`user_id`必須」400エラーは廃止）。
