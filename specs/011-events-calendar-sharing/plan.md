# Implementation Plan: グループカレンダーの作成・共有と予定作成

**Branch**: `011-events-calendar-sharing` | **Date**: 2026-08-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-events-calendar-sharing/spec.md`

## Summary

グループカレンダーの作成(`POST /api/calendars`)・招待コードでの参加(`POST /api/calendars/join`)・
予定の作成(`POST /api/events`)を、既存の`current_user`/`@login_required` + クエリ条件での
所有者・参加者確認(`010-secure-social-api`で確立したパターン、`is_calendar_member()`ヘルパーを流用)
で実装する。あわせて`apps/web`の`timeline`(group scope)・`mypage`画面をモックデータから
これらのAPI(および既存の`GET /api/calendars/{id}`・`GET /api/calendars/{id}/members`)に繋ぎ替える。

## Technical Context

**Language/Version**: Python 3.12(`apps/api`、Flask) / TypeScript, Next.js 16.3.0(`apps/web`)。

**Primary Dependencies**: 既存の`Flask-Login`/`Flask-SQLAlchemy`/`marshmallow`/`apispec`をそのまま利用。
招待コード生成には標準ライブラリ`secrets`を使う(新規外部依存なし)。

**Storage**: PostgreSQL 17(既存)。`calendars.invite_code`(既存カラム、現在は常にNULL)を初めて
実際に使う。`calendar_members`もこれまで一切書き込まれていなかった(`010`のPRマージ後に
`get_my_personal_calendar`が唯一の書き込み経路)。新規マイグレーションは不要。

**Testing**: `apps/api/tests/`(pytest、既存パターンを踏襲)。招待コードでの参加・重複参加・
不正コード・非参加者からの予定作成拒否・`is_private`予定の非表示を検証する。
`apps/web`側はブラウザでの手動確認(quickstart.md参照)。

**Target Platform**: Linuxコンテナ(devcontainer / Render)。`apps/web`の`next build`成否判定は
devcontainer固有の既知の問題によりホストOS/GitHub Actions CIを正とする(`010`から継続の運用)。

**Project Type**: web-service(`apps/web` + `apps/api`の2アプリ構成)。両アプリにまたがる。

**Performance Goals**: 既存エンドポイントと同等。招待コードの一意性チェックは`calendars.invite_code`
の`UNIQUE`制約(既存)にDB側でも守られるため、アプリ側の重複チェックは衝突時の再試行のみでよい。

**Constraints**: 憲章 原則III(NON-NEGOTIABLE)により権限なしは404固定。招待コードの誤りも
「コードが違う」以上の情報を返さない(存在有無を漏らさない)。

**Scale/Scope**: `apps/api`は`routes/calendars.py`(2エンドポイント追加)・`routes/events.py`
(1エンドポイント追加)・`schemas/calendar.py`(2スキーマ追加)。`apps/web`は`timeline`のgroup scope
と`mypage`ページの実装、`lib/calendars.ts`・`lib/events.ts`の拡張。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 該当ゲート | 判定 |
|---|---|---|
| III セキュリティ境界は`api`に一つだけ(NON-NEGOTIABLE) | 全エンドポイントに`@login_required`。参加者確認は`is_calendar_member()`(クエリ条件)。権限なし・無効な招待コードは404固定 | PASS |
| IV 秘密情報をクライアントへ出さない | 招待コードは秘密情報ではない(共有が前提の値)が、推測されにくいランダム値(`secrets`モジュール)を使う。新規の秘密鍵・トークンは追加しない | PASS |
| V 契約駆動の境界 | 新規3エンドポイント・2スキーマを`generate_openapi.py`に追加し`openapi.json`を再生成。`apps/web`は`npm run generate:api-types`で型を再生成 | PASS(Phase 1で対応をcontracts/に明記) |
| VI devcontainer固定 | 実装・依存インストール・テストはdevcontainer内で行う。例外は既存どおり(`next build`のみホスト/CI基準) | PASS |
| I 規約は1箇所にのみ書く | `docs/design.md` §7の画面別エンドポイント表(Timeline/Mypage)に新規エンドポイントを追記する | PASS(Phase 1のProject Structureにタスクとして明記) |

違反・トレードオフの正当化が必要な項目なし。Complexity Trackingは記入不要。

### Post-Design 再評価(Phase 1完了後)

Phase 1の設計成果物(data-model.md / contracts / quickstart.md)を反映しても、新規マイグレーション・
新規外部依存の追加・原則からの逸脱は無い。上表の全項目がPASS。

## Project Structure

### Documentation (this feature)

```text
specs/011-events-calendar-sharing/
├── plan.md              # このファイル
├── research.md          # Phase 0 出力
├── data-model.md         # Phase 1 出力
├── quickstart.md         # Phase 1 出力
├── contracts/
│   └── calendars-events-api.md   # Phase 1 出力
├── checklists/
│   └── requirements.md   # 既存(/speckit-specify 出力)
└── tasks.md              # Phase 2 出力(/speckit-tasks が生成、未作成)
```

### Source Code (repository root)

既存の`apps/api/app/{models,schemas,routes}`パターンを踏襲する。新規ファイルは追加しない
(既存ファイルへの追記のみ)。

```text
apps/api/app/
├── routes/
│   ├── calendars.py    # POST /calendars(グループ作成)・POST /calendars/join(招待コード参加)を追加
│   └── events.py       # POST /events(予定作成)を追加。既存のlist_eventsは変更なし
├── schemas/
│   └── calendar.py     # CalendarCreateSchema・CalendarJoinSchemaを追加

apps/api/generate_openapi.py   # 新規スキーマ・view_functions登録を追加
openapi.json                    # 再生成(生成物)
apps/web/src/lib/api-types.generated.ts   # 再生成(生成物)

apps/web/src/lib/
├── calendars.ts         # create・join を追加
└── events.ts            # create を追加

apps/web/src/app/
├── timeline/page.tsx    # group scopeを実APIに接続(グループ未所属時は作成/参加のUIを表示)
└── mypage/page.tsx      # グループ管理(作成・招待コード表示・参加)・メンバーランキングを実APIに接続

apps/web/src/components/mypage/
└── InviteCodeCard.tsx   # 招待コードの表示に加え、未所属時の「グループ作成」・「招待コードで参加」UIを追加

docs/design.md                  # §7 画面別エンドポイント表(Timeline/Mypage)に新規エンドポイントを追記
```

**Structure Decision**: 既存ディレクトリ構成の変更なし。`010-secure-social-api`で確立した
ファイル群・パターン(`is_calendar_member()`, `@login_required`, 404固定)をそのまま拡張する。

## Complexity Tracking

*違反なしのため記入なし*
