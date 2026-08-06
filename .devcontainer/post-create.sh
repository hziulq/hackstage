#!/usr/bin/env bash
# devcontainer の作成時に一度だけ実行される（devcontainer.json の postCreateCommand）
set -euo pipefail

WORKSPACE=/workspaces/hackstage

# ── git ───────────────────────────────────────────────
# マウント元（ホスト）と実行ユーザーの所有者が異なるため、
# これが無いと git の全操作が "dubious ownership" で失敗する
git config --global --add safe.directory "$WORKSPACE"

# ── Python 依存パッケージ ───────────────────────────────
# dev コンテナは .devcontainer/Dockerfile 由来で Python 本体しか持たない。
# Alembic（migrations/）は dev から実行する運用（CONTRIBUTING.md §5）なので、
# apps/api/requirements.txt を dev にも入れておく。
# --user なのは site-packages が root 所有で書けないため（sudo なしで完結させる）。
pip install --user -r "$WORKSPACE/apps/api/requirements.txt"

# ── Spec Kit の状態をブランチに追従させる ─────────────
# 規約は CONTRIBUTING.md §6。
# ブランチ名が NNN- 形式のときだけ設定し、それ以外では unset する。
# 無条件に設定すると main で SPECIFY_FEATURE_DIRECTORY=specs/main になり、
# /speckit-specify が明示値をそのまま使って specs/main/spec.md を作ってしまう。
#
# シェル起動時の一度きりでは git switch に追従しないため PROMPT_COMMAND に載せる。
SNIPPET_MARKER='# >>> hackstage: specify feature dir >>>'

if ! grep -qF "$SNIPPET_MARKER" "$HOME/.bashrc" 2>/dev/null; then
  cat >> "$HOME/.bashrc" <<'BASHRC'

# >>> hackstage: specify feature dir >>>
# ブランチ名から SPECIFY_FEATURE_DIRECTORY を導出する（CONTRIBUTING.md §6）
_hackstage_specify_feature() {
  local branch
  branch=$(git branch --show-current 2>/dev/null) || branch=''
  if [[ "$branch" =~ ^[0-9]{3,}- ]]; then
    export SPECIFY_FEATURE_DIRECTORY="specs/$branch"
  else
    unset SPECIFY_FEATURE_DIRECTORY
  fi
}
PROMPT_COMMAND="_hackstage_specify_feature${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
# <<< hackstage: specify feature dir <<<
BASHRC
  echo "[post-create] SPECIFY_FEATURE_DIRECTORY の導出を ~/.bashrc に追加しました"
fi

echo "[post-create] 完了"
echo
echo "  次の手順:"
echo "    .env が無い場合は  cp .env.example .env  してから値を埋めてください"
echo "    DB スキーマを作る:  cd apps/api && FLASK_APP=wsgi.py flask db upgrade"
echo "    規約は CONTRIBUTING.md / docs/design.md / .specify/memory/constitution.md"
