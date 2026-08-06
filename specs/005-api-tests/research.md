# Phase 0 Research: apiの自動テスト整備

## 1. テストフレームワーク

- **Decision**: `pytest`。`apps/api/requirements.txt`にバージョン固定で追加する。
- **Rationale**: Flaskエコシステムでの標準的な選択で、`Flask-SQLAlchemy` / `Flask-Login`との組み合わせ事例が豊富。追加の抽象化(`pytest-flask`等のプラグイン)は導入せず、`app.test_client()`を直接使う素のfixtureで十分(YAGNI。テスト対象がエンドポイント10本程度の小規模)。
- **Alternatives considered**: `unittest`(標準ライブラリ) — fixtureの表現力・パラメータ化のしやすさでpytestに劣り、Python生態系での採用実績もpytestが優勢。

## 2. テストとDBの分離方法

- **Decision**: 専用のテスト用データベースは作らない。既存の`db`サービス(開発用Postgres)に対し、テストごとに接続をSAVEPOINT(ネストしたトランザクション)で囲み、テスト終了時に必ずロールバックする(SQLAlchemy 2.0 / Flask-SQLAlchemy 3.x で文書化されている「外部トランザクションへの参加」パターン)。
- **Rationale**: FR-007(開発用DBを汚染しない)を満たす方法は主に2つある。(a) `hackstage_test`のような専用DBを新設する、(b) 既存DBに接続しつつ物理的にコミットさせない。(a)は`compose.yaml`・環境変数・CI設定の追加が必要になり、経験の浅いメンバーが増える設定項目が増える。(b)はアプリケーションコード側(`conftest.py`)だけで完結し、新しい環境変数やDocker構成の変更が不要。憲章 原則VI(devcontainer固定)・原則I(規約の一元化)の観点でも変更箇所が少ない(b)を採用する。
- **Alternatives considered**: 専用テストDB(`hackstage_test`)を作り`db.create_all()`/`drop_all()`する案 — テスト間の分離は明確だが、`.env.example`・`compose.yaml`・README変更が必要になり、本feature(テスト整備そのもの)のスコープに対して構成変更のコストが不釣り合いに大きい。将来テスト規模が増えて並列実行(pytest-xdist等)が必要になった時点で再検討する。

## 3. Flask-Limiter(レート制限)のテスト間干渉

- **Decision**: `conftest.py`に、各テストの前に`limiter`のストレージをリセットするfixtureを追加する(`limiter.reset()`、または内部の`storage`を再生成する)。レート制限のテスト(`test_auth_rate_limit.py`)は他の認証テストと同じログイン試行回数のカウンタを共有しないよう、明示的にリセットしてから閾値超過を検証する。
- **Rationale**: `Flask-Limiter`の既定ストレージは`memory://`(プロセス内)であり、テスト実行順序によって直前のテストのログイン失敗回数が残ったまま次のテストの1回目からブロックされる、という意図しない失敗(spec.mdのEdge Case)が起きる。テストごとにリセットすることで、各テストが自分の閾値検証にのみ責任を持つようにする。
- **Alternatives considered**: レート制限を一切テストせずスキップする — spec.md FR-004(User Story 3)で明示的に要求されているため不採用。

## 4. ログイン状態の再現方法

- **Decision**: `app.test_client()`をそのまま使う。Flaskのテストクライアントは同一クライアントインスタンス内でCookie(セッション)を自動的に保持するため、`client.post("/api/login", ...)`の後に同じ`client`で`client.get("/api/me")`を呼べば、`quickstart.md`のcurlで手動管理していたCookie jarの代わりになる。
- **Rationale**: 追加のライブラリやヘルパーを書かずに`quickstart.md`のシナリオをそのまま自動テスト化できる。

## 5. テスト用ユーザー・Todoの作成

- **Decision**: `conftest.py`に、テスト内で使う利用者を作成するヘルパー関数(例: `create_user(email, password, display_name)`)を用意する。メールアドレスは各テスト関数内でユニークな値を明示的に指定する(モジュールレベルの共有定数にしない)。
- **Rationale**: 2番目のResearch項目(SAVEPOINTロールバック)により、テスト間でデータは残らないため重複メールを気にする必要は薄いが、テスト内の可読性(どの利用者がそのテストのものか)のため、テストごとに明示的に作成する。

## 未解決のNEEDS CLARIFICATION

なし。spec.mdのAssumptionsで技術的な実現手段は本Phaseで決定するとされており、上記で全て決定済み。
