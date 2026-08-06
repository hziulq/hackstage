# Implementation Plan: 掲示板・目標・カレンダーAPIの認証統合

**Branch**: `010-secure-social-api` | **Date**: 2026-08-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-secure-social-api/spec.md`

## Summary

`008-auth-todo-api`で追加された`posts`/`goals`/`calendars`/`events`/`reactions`の各エンドポイント
(現状はクライアントが送る`user_id`をそのまま信用する暫定実装)を、`003-user-auth`で確立済みの
`flask_login`の`current_user`/`@login_required` + クエリ条件での所有者確認(`todos.py`と同じパターン)
に置き換える。あわせて`008-web-auth-openapi-types`のログイン/登録UIと`proxy.ts`を反映し、
`openapi.json`・`apps/web`側の生成型を更新後の契約と一致させる。

`008-auth-todo-api`と`008-web-auth-openapi-types`はいずれも`preview`未統合のリモートブランチ
だったため、本feature作業の前提として両方を`010-secure-social-api`にマージ済み(コンフリクトなし)。
本ドキュメントはマージ後のコードを起点に計画する。

## Technical Context

**Language/Version**: Python 3.12(`apps/api`) / TypeScript, Next.js 16.3.0(`apps/web`)。
spec.mdの入力文中の「FastAPI」は誤り。実際は**Flask**(`flask_login`ベース)。

**Primary Dependencies**: `apps/api`側は既存の`Flask-Login`/`Flask-SQLAlchemy`/`marshmallow`/
`Flask-Limiter`/`apispec`をそのまま利用(新規依存追加なし)。`apps/web`側も既存の
`openapi-typescript`(型生成)をそのまま利用。

**Storage**: PostgreSQL 17(既存)。`posts`/`goals`/`goal_milestones`/`calendars`/
`calendar_members`/`events`/`reactions`のテーブル・カラムは`008-auth-todo-api`で確定済みで、
本featureはスキーマ変更・マイグレーション追加を行わない(認証・認可ロジックのみ変更)。

**Testing**: `apps/api/tests/`(pytest、`005-api-tests`のパターンを踏襲)。未ログイン401・
他人データへのアクセス404・`openapi.json`再生成の再現性を検証する。`apps/web`側はブラウザでの
手動確認(quickstart.md参照、`006-openapi-generation`同様に自動E2Eは対象外)。

**Target Platform**: Linuxコンテナ(devcontainer / Render)。**注記**: このdevcontainer
(Docker Desktop for Windows + WSL2)では`apps/web`の`next build`がdevcontainer固有の問題で
失敗することが既知(`next dev`・型チェック・lintは問題なし)。`next build`の成否判定は
ホストOSまたはGitHub Actions CI(`web-ci.yml`)を正とする。

**Project Type**: web-service(`apps/web` + `apps/api`の2アプリ構成)。両アプリにまたがる。

**Performance Goals**: 既存エンドポイントと同等(認可判定はインデックス済みカラム
(`id`, `user_id`, `calendar_id`)へのクエリ条件追加のみで、追加のN+1やフルスキャンを発生させない)。

**Constraints**: 憲章 原則III(NON-NEGOTIABLE)により、権限なしは**404固定**(403は使わない)。
これはspec.mdのAcceptance Scenarios/Edge Casesの「403または404」「403(または401)」という記述と
矛盾するため、本Constitution Checkで404に一本化する(詳細はresearch.md §2)。

**Scale/Scope**: `posts`/`goals`/`calendars`/`events`/`reactions`の全エンドポイント
(一覧5ファイル、既存11エンドポイント+新規該当分)。`apps/web`側はログイン/登録UIと
`proxy.ts`の統合のみ(画面のAPI接続自体は別feature、spec.md Assumptions参照)。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 該当ゲート | 判定 |
|---|---|---|
| III セキュリティ境界は`api`に一つだけ(NON-NEGOTIABLE) | 全保護エンドポイントに`@login_required`。所有者確認はクエリ条件(`filter_by(id=..., user_id=current_user.id)`、`todos.py`と同じ)。**権限なしは404固定、403は使わない**(spec.mdの「403または404」は本Checkで404に統一し解消する) | PASS(design.md §7の既定「権限なし→404」に統一) |
| IV 秘密情報をクライアントへ出さない | 変更なし(既存のHttpOnly Cookieセッションをそのまま使う。新規の秘密値・トークンは追加しない) | PASS |
| V 契約駆動の境界 | `posts`/`goals`/`calendars`/`events`/`reactions`を`generate_openapi.py`の`view_functions`に追加し`openapi.json`を再生成。`apps/web`は`npm run generate:api-types`で型を再生成。手書き型追加は禁止 | PASS(Phase 1で対応をcontracts/に明記) |
| VI devcontainer固定 | 実装・依存インストール・テストはdevcontainer内で行う。**例外**: `apps/web`の`next build`(ビルド成否の最終判定)のみdevcontainer固有の既知の問題によりホスト/CIを正とする(既存の合意事項、`008-render-deploy-prep`で確立済み) | PASS(既存の例外運用を継続。新規の逸脱ではない) |
| I 規約は1箇所にのみ書く | `docs/design.md` §8に`middleware.ts`と記載されているが、実装(`008-web-auth-openapi-types`)は Next.js 16の命名規則変更により`proxy.ts`。本feature内で`docs/design.md`側を先に修正してから統合を完了とする | PASS(Phase 1のProject Structureにタスクとして明記) |

違反・トレードオフの正当化が必要な項目なし。Complexity Trackingは記入不要。

### Post-Design 再評価(Phase 1完了後)

Phase 1の設計成果物(data-model.md / contracts / quickstart.md)を反映しても、新規マイグレーション・
新規外部依存の追加・原則からの逸脱は無い。上表の全項目がPASS。

## Project Structure

### Documentation (this feature)

```text
specs/010-secure-social-api/
├── plan.md              # このファイル
├── research.md          # Phase 0 出力
├── data-model.md         # Phase 1 出力
├── quickstart.md         # Phase 1 出力
├── contracts/
│   └── social-api.md     # Phase 1 出力
├── checklists/
│   └── requirements.md   # 既存(/speckit-specify 出力)
└── tasks.md              # Phase 2 出力(/speckit-tasks が生成、未作成)
```

### Source Code (repository root)

`docs/design.md` §3 で確定済みの`apps/api/app/{models,schemas,routes}`パターンを踏襲する。
新規ファイルは追加しない(既存の`008-auth-todo-api`由来のファイルを変更するのみ)。

```text
apps/api/app/
├── routes/
│   ├── posts.py       # @login_required追加、user_id取得元をcurrent_user.idに変更、
│   │                   # comments作成も同様。calendar_id指定時はメンバーシップ確認を追加
│   ├── goals.py        # @login_required追加、user_id取得元をcurrent_user.idに変更、
│   │                   # クエリパラメータ user_id を廃止
│   ├── events.py       # @login_required追加、calendar_idのメンバーシップ確認、
│   │                   # is_privateな予定は本人以外に見せないフィルタを追加(spec.md Key Entities)
│   ├── reactions.py    # @login_required追加、user_id取得元をcurrent_user.idに変更
│   └── calendars.py    # @login_required追加、参加者(CalendarMember)本人以外は404
├── schemas/
│   ├── post.py         # PostSchema/PostCommentSchemaのuser_idをdump_onlyに変更(todo.pyと同じ)
│   ├── goal.py          # GoalSchema/GoalCreateSchemaのuser_idをdump_onlyに変更
│   ├── event.py         # EventSchemaのuser_idをdump_onlyに変更
│   └── reaction.py      # ReactionSchemaのuser_idをdump_onlyに変更
│   # schemas/calendar.py は変更なし(クライアントから作成しないため user_id フィールド無し)

apps/api/generate_openapi.py   # posts/goals/events/reactions/calendarsのスキーマ・view_functions登録を追加
openapi.json                    # 再生成(生成物、手動編集禁止)
apps/web/src/lib/api-types.generated.ts   # openapi.json再生成後に再生成(生成物、手動編集禁止)

docs/design.md                  # §8「web: middleware.ts」を「web: proxy.ts」に修正(原則I)
```

**Structure Decision**: 既存ディレクトリ構成の変更なし。`008-auth-todo-api`で追加済みの
ファイル群を`003-user-auth`(`todos.py`)確立済みのパターンに合わせて修正するのみ。
新規ディレクトリ・新規依存の追加は無い。

## Complexity Tracking

*違反なしのため記入なし*
