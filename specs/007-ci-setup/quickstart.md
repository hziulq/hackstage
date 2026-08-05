# Quickstart: CIワークフローの動作確認

`dev`コンテナ内で、GitHub Actions上と同じコマンドをローカルで再現して確認する
(GitHub Actions自体の実行はPRを作らないと確認できないため、まずローカルで各ジョブの
コマンドが成功することを確認する)。

## Lintジョブの再現

```bash
pip install --user ruff
cd apps/api
ruff check .
```

**期待結果**: 既存コードに対してエラーなく完了する(既定ルールセットで開始するため、
導入時点でエラーが出ないことを確認する)。

## テストジョブの再現

```bash
cd apps/api
python -m pytest
```

**期待結果**: `005-api-tests`で整備した全テストがパスする。

## openapi.json生成差分チェックジョブの再現

```bash
cd apps/api
python generate_openapi.py
git diff --exit-code ../../openapi.json
```

**期待結果**: 実装(routes/*.py)と`openapi.json`が一致していれば差分なし(終了コード0)。

## PRでの確認(実際のCI実行)

1. 本featureのブランチをpushし、PRを作成する
2. GitHub ActionsのCheck一覧に`lint` / `test` / `openapi-check`の3ジョブが表示されることを確認する
3. 意図的にLintエラーまたはテスト失敗を混入させたコミットを追加し、該当ジョブが失敗(赤)で表示されつつ、
   PRのマージボタンが無効化されないことを確認する
4. 混入させた変更を取り除く(またはrevertする)
