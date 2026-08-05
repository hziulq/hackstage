# Quickstart: apiの自動テストの動作確認

`dev`コンテナ内で実行する(憲章 原則VI)。`db`サービスが起動していること。

## 前提: 依存関係の反映

```bash
# dev コンテナ内
pip install --user -r apps/api/requirements.txt
```

## テストスイートの実行

```bash
cd apps/api
python -m pytest
```

**期待結果**: `test_auth.py` / `test_auth_rate_limit.py` / `test_todos.py`の全テストがパスする。

## 回帰検知の確認(意図的に不具合を混入させて確認する場合)

以下はレビュー時の動作確認用の手順で、実装には含めない。

1. `apps/api/app/models/user.py`の`check_password`を常に`True`を返すように一時的に変更する
2. `python -m pytest apps/api/tests/test_auth.py`を実行し、ログイン失敗系のテストが失敗することを確認する
3. 変更を元に戻す

## テスト後のDB確認

```bash
# dev コンテナ内。テスト実行前後でカウントが変わっていないことを確認する
psql "$DATABASE_URL" -c "SELECT count(*) FROM users;"
psql "$DATABASE_URL" -c "SELECT count(*) FROM todos;"
```

**期待結果**: テストスイート実行前後で件数が変化しない(SAVEPOINTロールバックにより、テストで作成した
データが残らないため)。
