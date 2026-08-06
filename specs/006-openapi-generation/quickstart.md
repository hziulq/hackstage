# Quickstart: openapi.jsonの生成の動作確認

`dev`コンテナ内で実行する(憲章 原則VI)。`db`サービスの起動は不要(生成にDB接続は使わない)。

## 前提: 依存関係の反映

```bash
# dev コンテナ内
pip install --user -r apps/api/requirements.txt
```

## 生成の実行

```bash
cd apps/api
python generate_openapi.py
```

**期待結果**: リポジトリルート直下に`openapi.json`が生成・更新される。

## 内容の確認

```bash
# 対象エンドポイントが揃っていることを確認する
python -c "
import json
spec = json.load(open('../../openapi.json'))
print(sorted(spec['paths'].keys()))
"
```

**期待結果**: `/api/health`, `/api/hello`, `/api/login`, `/api/logout`, `/api/me`, `/api/register`,
`/api/todos`, `/api/todos/{todo_id}` が含まれる。

## 再実行可能性の確認(FR-006)

```bash
cd apps/api
python generate_openapi.py
git diff --stat ../../openapi.json
```

**期待結果**: コードを変更していない状態で再実行した場合、差分が出ない(同じ入力から同じ出力)。

## テストでの確認

```bash
cd apps/api
python -m pytest tests/test_openapi_generation.py
```

**期待結果**: 生成結果の構造(対象エンドポイントの網羅・妥当なJSON形式)を検証するテストがパスする。
