# Phase 0 Research: グループカレンダーの作成・共有と予定作成

## 1. 招待コードの生成方式

- **Decision**: 標準ライブラリ`secrets.token_urlsafe(6)`(約8文字、英数字+`-`/`_`)を使う。
  `Calendar.invite_code`(既存カラム、`String(32)` unique)への衝突時は再生成して最大10回リトライする。
- **Rationale**: 新規外部依存を追加せず、`docs/design.md`にある秘密情報管理の対象外(招待コードは
  共有前提の値であり機密情報ではない)であることを踏まえても、推測されにくいランダム値であれば
  十分。既存カラムが`unique=True`のため、DB側でも重複は最終的に防止される。
- **Alternatives considered**: 連番・短い数字コード — 推測されやすく、招待コードの性質(共有先だけが
  参加できる)に反する。UUID全体 — カラム長(32文字)に対して冗長。

## 2. 招待コード参加時のレスポンス方針

- **Decision**: 既存メンバーなら`200`(冪等)、新規参加なら`201`を返す。無効なコードは`404`
  (`invalid_invite_code`という汎用コードのみ、存在有無の詳細は返さない)。
- **Rationale**: `reactions.py`の`create_reaction`(既存レコードがあれば200で上書き、無ければ201で
  新規作成)と同じ「upsert的操作」のレスポンス規約にならい、新しいパターンを増やさない
  (FR-005: 重複参加はエラーにしない)。憲章 原則III「権限が無い場合は404」に従い、無効な
  コードも403ではなく404にする。

## 3. 予定作成時の参加者確認

- **Decision**: `todos.py`/`010-secure-social-api`で確立済みの`is_calendar_member()`ヘルパー
  (`routes/utils.py`、`010`で追加済み)をそのまま使う。`EventSchema`は`010`時点で既に
  `calendar_id`必須・`user_id`は`dump_only`になっているため、スキーマ変更は不要。
- **Rationale**: 既存パターンの再利用。新規のコードパスを増やさない。

## 4. グループ作成時のオーナー登録

- **Decision**: `calendars.py`の`get_my_personal_calendar`(個人カレンダーのget-or-create、`010`で
  追加済み)と同じトランザクション手順(`Calendar`を`flush`してIDを確定させてから`CalendarMember`を
  追加、最後に`commit`)を踏襲する。
- **Rationale**: 既存の書き込みパターンをそのまま複製すればよく、新しい設計判断は不要。

## 5. `apps/web`側のグループ状態の扱い(「所属グループ」が無い場合)

- **Decision**: `mypage`・`timeline`のgroup scopeは「自分が参加している最初のグループカレンダー」
  を対象とする(既存モックが単一グループのUIを前提にしているため)。所属グループが無い場合は
  グループ作成フォームと招待コード参加フォームの両方を表示し、いずれかの操作でグループに
  所属した状態に遷移する。
- **Rationale**: spec.mdは複数グループの管理UIを要求していない(Key Entitiesは単数のGroupの
  作成・参加のみを扱う)。既存の`GroupInfo`型・`ScopeTabs`・`InviteCodeCard`のUIも単一グループの
  前提で作られており、UIの大幅な再設計は本featureのスコープ外(Assumptions参照)。
- **Alternatives considered**: 複数グループの切り替えUIを新設する — spec.mdの要求を超える
  過剰実装であり、既存デザインとの整合も取れないため見送る。
- **対象APIの決定**: `GET /api/calendars/{id}/members`等で「自分が参加しているグループ」を直接
  列挙するエンドポイントは無い。本feature内では、グループ作成・参加のレスポンス(`Calendar`)を
  クライアント側の状態(ローカルストレージ、既存の`useLocalStorageState`と同じ仕組み)に
  `calendar_id`として保持し、以後のアクセスに使う(既存の`personalCalendarId`と同じ扱い方)。
  ページ再訪時に一覧取得エンドポイントが無いことの限界は Edge Cases として明記する。

## 6. 追加で見つかった制約(Edge Case)

- **利用者が参加しているグループを後から一覧できない**: 上記5の設計上、`calendar_id`を
  ブラウザのlocalStorageに保持する方式のため、別のブラウザ・別デバイスからは
  「自分の所属グループ」を再取得する手段が無い(個人カレンダーは`GET /api/calendars/mine`が
  あるが、グループカレンダーには同等のエンドポイントが無い)。本feature後の既知の制約として
  記録し、必要になった時点で「自分が参加しているカレンダー一覧」エンドポイントを追加検討する
  (Assumptions/Edge Casesに追記)。

## 未解決のNEEDS CLARIFICATION

なし。spec.mdのチェックリストで全項目解消済み。
