#!/usr/bin/env bash
# devcontainer の作成時に一度だけ実行される（devcontainer.json の postCreateCommand）
set -euo pipefail

WORKSPACE=/workspaces/nextstage

# ── git ───────────────────────────────────────────────
# マウント元（ホスト）と実行ユーザーの所有者が異なるため、
# これが無いと git の全操作が "dubious ownership" で失敗する
git config --global --add safe.directory "$WORKSPACE"

# ── Spec Kit の状態をブランチに追従させる ─────────────
# 規約は CONTRIBUTING.md §6。
# ブランチ名が NNN- 形式のときだけ設定し、それ以外では unset する。
# 無条件に設定すると main で SPECIFY_FEATURE_DIRECTORY=specs/main になり、
# /speckit-specify が明示値をそのまま使って specs/main/spec.md を作ってしまう。
#
# シェル起動時の一度きりでは git switch に追従しないため PROMPT_COMMAND に載せる。
SNIPPET_MARKER='# >>> nextstage: specify feature dir >>>'

if ! grep -qF "$SNIPPET_MARKER" "$HOME/.bashrc" 2>/dev/null; then
  cat >> "$HOME/.bashrc" <<'BASHRC'

# >>> nextstage: specify feature dir >>>
# ブランチ名から SPECIFY_FEATURE_DIRECTORY を導出する（CONTRIBUTING.md §6）
_nextstage_specify_feature() {
  local branch
  branch=$(git branch --show-current 2>/dev/null) || branch=''
  if [[ "$branch" =~ ^[0-9]{3,}- ]]; then
    export SPECIFY_FEATURE_DIRECTORY="specs/$branch"
  else
    unset SPECIFY_FEATURE_DIRECTORY
  fi
}
PROMPT_COMMAND="_nextstage_specify_feature${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
# <<< nextstage: specify feature dir <<<
BASHRC
  echo "[post-create] SPECIFY_FEATURE_DIRECTORY の導出を ~/.bashrc に追加しました"
fi

echo "[post-create] 完了"
echo
echo "  次の手順:"
echo "    .env が無い場合は  cp .env.example .env  してから値を埋めてください"
echo "    規約は CONTRIBUTING.md / docs/design.md / .specify/memory/constitution.md"
