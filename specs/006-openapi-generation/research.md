# Phase 0 Research: openapi.jsonの生成

## 1. OpenAPI生成ライブラリ

- **Decision**: `apispec` + `apispec-webframeworks`(`FlaskPlugin`) + `apispec.ext.marshmallow`(`MarshmallowPlugin`)。
- **Rationale**: 既存の`apps/api`は素のFlask Blueprint + marshmallowで実装されており(`flask-smorest`等の統合フレームワークは使っていない)、`apispec`は既存のBlueprint・View関数・marshmallow Schemaを変更せずに後付けでOpenAPIスキーマを生成できる。各Viewのdocstringに軽量なYAMLを追記するだけで済み、既存ルート(`auth.py`, `todos.py`, `health.py`, `hello.py`)の実装ロジックには触れない。
- **Alternatives considered**: `flask-smorest`への移行(Blueprint定義そのものをflask-smorest流に書き換える) — 既存の全ルートファイルを書き換える必要があり、本feature(契約の生成)のスコープに対して変更範囲が不釣り合いに大きい(YAGNI)。`flasgger` — Swagger 2.0中心で、OpenAPI 3系への対応がapispecに比べて弱い。

## 2. OpenAPIバージョン

- **Decision**: OpenAPI 3.0.3。
- **Rationale**: `web`側の型生成(`docs/design.md` §7「`web`は`openapi.json`からTypeScript型を生成する」)で使われる可能性が高い`openapi-typescript`等の主要ツールは3.0系のサポートが最も枯れている。3.1系は`apispec`側のサポートも新しく、`web`側ツールチェーンとの相性リスクを避ける。

## 3. スキーマ記述の方法

- **Decision**: 各View関数のdocstringに、apispecの規約に沿ったYAMLブロックを追記する(`---`区切り)。`RegisterSchema`/`LoginSchema`/`UserSchema`/`TodoSchema`は`spec.components.schema(...)`で一度だけ登録し、各Viewのdocstringから`$ref`で参照する。
- **Rationale**: 既存のmarshmallow Schemaをそのまま再利用でき(FR-002)、スキーマの二重管理を避けられる(憲章 原則V)。

## 4. 生成スクリプトの配置と実行方法

- **Decision**: `apps/api/generate_openapi.py`を新規作成する。`python generate_openapi.py`(devコンテナ内、`apps/api`ディレクトリ)で実行し、`create_app()`のFlaskインスタンスからURLルールを走査して`openapi.json`をリポジトリルート直下に書き出す。
- **Rationale**: `docs/design.md` §3で`openapi.json`の位置(リポジトリルート)は既に予約済み。生成にDB接続は不要(View関数を実際には呼び出さず、ルーティング情報とdocstringのみを読む)なため、`db`サービスの起動は生成の前提にしない。
- **Alternatives considered**: Flask CLIカスタムコマンド(`flask openapi generate`)として実装する案 — 実行方法が増えるだけで、素のPythonスクリプトより複雑さが増す割に利点が薄い(YAGNI)。

## 5. 出力の安定性(FR-006: 再実行可能性)

- **Decision**: スクリプト内でSchema登録・View登録の順序を固定(コード上の並び順)し、`json.dump(..., indent=2, ensure_ascii=False)`で出力する。
- **Rationale**: 登録順序を固定すれば、コードを変更しない限り`apispec`の`to_dict()`は同じキー順を返す。`ensure_ascii=False`で日本語の説明文がエスケープされず、`git diff`で人間が読みやすい差分になる。

## 6. 対象エンドポイントの範囲

- **Decision**: 実装済みの`/api/health`, `/api/hello`, `/api/register`, `/api/login`, `/api/logout`, `/api/me`, `/api/todos`(CRUD)のみを対象にする。`docs/design.md`「画面別エンドポイント(検討中)」にある未実装のエンドポイント(posts/goals/events等)はコードが存在しないため対象外(spec.mdのEdge Caseの通り)。
- **Rationale**: 実装と契約の食い違いを防ぐのが本featureの目的であり、存在しないエンドポイントを先に契約化すると逆に「契約はあるが実装が無い」食い違いを生む。

## 未解決のNEEDS CLARIFICATION

なし。
