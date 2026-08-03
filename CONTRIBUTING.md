# 開発手順

**作業を始める前に読む文書。** 守るべき原則は `.specify/memory/constitution.md`（憲章）、
設計値は `docs/design.md` にある。本文書は「どう作業するか」だけを扱う。

Spec Kit（SDD）の利用は**任意**。§6 は使う人だけ読めばよい。

---

## 1. 環境を立ち上げる

開発は devcontainer 内で行う（憲章 原則 VI）。ホストで直接 `npm install` / `pip install` はしない。

手順は `README.md` にある。要点だけ:

1. `cp .env.example .env` して `POSTGRES_PASSWORD` と `SECRET_KEY` を埋める
   （飛ばすと `db` が起動に失敗する）
2. VS Code で "Reopen in Container" を選ぶ
3. `dev` と `db` が起動し、`dev` コンテナの中に入る

`web` / `api` サービスは `apps/**` の骨格が揃うまで `compose.yaml` の `profiles: [app]` で
無効にしてある。それまでは `dev` コンテナ内で `npm run dev` / `flask run` を起動すれば
ホストの `localhost:3000` / `localhost:8000` から見える。有効化の手順は `compose.yaml` のコメント。

---

## 2. ブランチとコミット

| 項目 | 規約 |
|---|---|
| ブランチ名 | `NNN-slug`（例: `003-user-profile`） |
| `main` への直接 push | 禁止。すべて PR 経由 |
| 1 ブランチの範囲 | 1 機能 / 1 修正。複数機能を混ぜない |

担当ごとの成果物と越境時の扱いは `docs/design.md` §13 にある。

```
main
 ├ 003-user-profile   ← Aさん
 ├ 004-post-crud      ← Bさん
 └ 005-render-preview ← Cさん
```

feature を始めるとき:

```powershell
git switch main
git pull
git fetch origin          # 番号の基準を最新にする
# 使う番号とスラッグを Issue / チャットで宣言する
git switch -c 003-user-profile
```

**番号は宣言してから取る。** 連番は `specs/` の最大値 +1 で決まるため、同時に採番すると重複する。
重複した場合、後から push する側がリネームして解消する。

---

## 3. PR を出す

- レビューは**憲章への適合とセキュリティチェックリストのみ**で判定する。
  spec の有無は問わない（憲章 Governance）。
- 原則に反する実装を含める場合、対象箇所・理由・解消条件を PR に記録する。記録が無い違反は却下。

同一 PR に含める必要があるもの:

| 変更 | 同時に含めるもの |
|---|---|
| 環境変数の追加 | `.env.example` / `compose.yaml` / `render.yaml` の**3 箇所** |
| `openapi.json` の変更 | `web` 側の型再生成（または追随タスクの明記） |
| `.devcontainer/` の変更 | **専用 PR にする**（他の変更を混ぜない） |
| 憲章の変更 | **専用 PR にする**（他の変更を混ぜない） |

---

## 4. 共有ファイルの扱い

機能ごとのファイル（`apps/**` の担当範囲、`specs/NNN-slug/`）は衝突しない。
衝突するのは以下の共有物だけ。

| ファイル | 規約 |
|---|---|
| `openapi.json` | 生成物。**手動マージ禁止**。再生成して解決する |
| `migrations/**` | §5 に従う |
| `.specify/memory/constitution.md` | 専用 PR。機能 PR に混ぜない |
| `.specify/templates/` `.specify/scripts/` | 共有資産。個人ブランチで変えない |
| Spec Kit 本体のバージョン | 専用 PR。全員が同じバージョンを使う |
| `.claude/` | 共有する。`settings.local.json` は `.gitignore` |

### `.gitignore` の必須エントリ

```
.env
node_modules
__pycache__
.next
.specify/feature.json
.claude/settings.local.json
```

---

## 5. 並行マイグレーション（Alembic）

2 つのブランチが同じ親リビジョンから別のマイグレーションを作ると、**git は衝突を報告しないが**
マージ後に head が 2 つになり `alembic upgrade head` が `Multiple head revisions` で失敗する。

- マイグレーションを含む PR は、出す前に最新の `main` を取り込む
- 後から `main` に入る側が、自分のリビジョンの `down_revision` を相手のリビジョンへ付け替える
  （履歴を直線に保つ）。`alembic merge heads` は履歴が分岐したまま残るため既定としない
- 1 つの PR に含めるマイグレーションは、可能な限り 1 リビジョンにまとめる

Alembic は `dev` コンテナから実行する（`db:5432` に到達できる）。

---

## 6. Spec Kit を使う場合（任意）

使わない場合はこの節を飛ばしてよい。仕様を手書きする場合も、置き場所は `specs/NNN-slug/` に揃える。

### 前提

`dev` コンテナに `pwsh` が入っていること（理由と設定は `docs/design.md` §10）。

### feature の作り方

ディレクトリ名を**先に決めて固定してから**実行する。

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-user-profile'
/speckit-specify ユーザープロフィール編集機能
git switch -c 003-user-profile      # ブランチは自分で切る
```

- `/speckit-specify` は `create-new-feature.ps1` を呼ばないため、**`-Number` は使えない**。
  `SPECIFY_FEATURE_DIRECTORY` が唯一の指定手段（明示値が最優先で使われる）。
- 固定しないとスラッグもモデルが決めるため、宣言したブランチ名と食い違う。
- `/speckit-specify` はブランチを作らない（git 拡張が未インストール）。

以降は自分のブランチで完結する。

```powershell
/speckit-plan
/speckit-tasks
/speckit-implement
```

### 状態ファイルの扱い

Spec Kit は「現在の feature」を `.specify/feature.json` に **1 つだけ**書く。
これは `.gitignore` 対象。コミットすると他人の feature を指した状態が配布され、
`/speckit-plan` が別人の spec を書き換える。

`.gitignore` されているため `git switch` しても状態が追従しない。そのため
**devcontainer 側で自動導出するようにしてある**（`.devcontainer/post-create.sh` が
`~/.bashrc` に仕込む）。各自で設定する必要はない。

```
branch = 現在のブランチ名
if branch が ^[0-9]{3,}- に一致する:  SPECIFY_FEATURE_DIRECTORY = "specs/<branch>"
else:                                 SPECIFY_FEATURE_DIRECTORY を unset
```

**無条件に設定してはいけない。** `main` にいるとき値が `specs/main` になり、`/speckit-specify` は
明示値をそのまま使うため `specs/main/spec.md` を生成してしまう。この分岐を消さないこと。

手動で別の feature を指したいときは、シェルでその場だけ上書きする:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-user-profile'
```

clone 直後に `/speckit-plan` を実行すると feature 未設定エラーになる。これは正常。上記で設定する。

### 1 ブランチに feature ディレクトリは 1 つ

2 つ以上作ると状態の指す先が曖昧になる。
