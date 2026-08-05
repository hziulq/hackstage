# Quickstart: ユーザー認証の動作確認

`apps/api/README.md`の運用に従い、確認は **`dev`コンテナ内**から `http://api:8000` に対して行う
（`api`はexposeのみでホストに公開していないため、ホスト側からは直接届かない）。

## 前提: 依存関係の反映

`requirements.txt`に`Flask-Login`/`argon2-cffi`/`Flask-Limiter`を追加した後:

```bash
# dev コンテナ内（flask db 等をdevから実行するため、devにも requirements を反映する）
pip install --user -r apps/api/requirements.txt
```

```bash
# ホスト側ターミナル（dev コンテナには Docker CLI が無いため）
docker compose build api
docker compose up -d api
```

## シナリオ1: 登録 → ログイン → 自分の情報取得 → ログアウト

```bash
# dev コンテナ内
COOKIE_JAR=$(mktemp)

# 1. 新規登録(FR-001) — 201 Created
curl -s -i -X POST http://api:8000/api/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"correct-horse","display_name":"山田太郎"}'

# 2. ログイン(FR-003, FR-004) — 200 OK + Set-Cookie
curl -s -i -c "$COOKIE_JAR" -X POST http://api:8000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"correct-horse"}'

# 3. 自分の情報取得(FR-006) — 200 OK、Cookie経由で識別される
curl -s -i -b "$COOKIE_JAR" http://api:8000/api/me

# 4. ログアウト(FR-005) — 204 No Content
curl -s -i -b "$COOKIE_JAR" -X POST http://api:8000/api/logout

# 5. ログアウト後の /api/me(FR-007) — 401 Unauthorized になること
curl -s -i -b "$COOKIE_JAR" http://api:8000/api/me
```

**期待結果**: 手順1で201、手順2で200+`Set-Cookie`ヘッダ、手順3で`{"email":"student@example.com",...}`、
手順4で204、手順5で401 `{"error":{"code":"unauthorized",...}}`。

## シナリオ2: 重複登録の拒否(FR-002)

```bash
curl -s -i -X POST http://api:8000/api/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"another-pass","display_name":"別名"}'
```

**期待結果**: 400 `{"error":{"code":"invalid_request",...}}`。

## シナリオ3: ログイン失敗時の一律エラー(FR-008)

```bash
# 存在しないメール
curl -s -i -X POST http://api:8000/api/login \
  -H 'Content-Type: application/json' -d '{"email":"nobody@example.com","password":"x"}'

# 登録済みメール + 誤ったパスワード
curl -s -i -X POST http://api:8000/api/login \
  -H 'Content-Type: application/json' -d '{"email":"student@example.com","password":"wrong"}'
```

**期待結果**: どちらも同一の401レスポンス（`code`・`message`が一致し、原因を判別できないこと）。

## シナリオ4: レート制限(FR-009)

```bash
for i in $(seq 1 6); do
  curl -s -o /dev/null -w '%{http_code}\n' -X POST http://api:8000/api/login \
    -H 'Content-Type: application/json' -d '{"email":"student@example.com","password":"wrong"}'
done
```

**期待結果**: 設定した閾値（1分あたり5回、research.md参照）を超えた時点から`429`が返ること。

## シナリオ5: `/api/todos` の認証必須化（副作用の確認）

```bash
# 未ログインでの一覧取得 — 401 になること（旧: user_id必須の400ではない）
curl -s -i http://api:8000/api/todos

# ログイン後は current_user.id のTodoのみが対象になること
curl -s -i -b "$COOKIE_JAR" http://api:8000/api/todos
```

## 詳細な契約

各エンドポイントのリクエスト/レスポンス形式は [contracts/auth-api.md](./contracts/auth-api.md) を参照。
