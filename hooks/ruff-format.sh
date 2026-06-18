#!/usr/bin/env bash
# PostToolUse フック: Claude が編集した .py を Ruff で整形・自動修正する。
# commit 時に ruff-format が走って再 stage になる摩擦を、編集直後に潰すのが狙い。
#
# 前提: uv が使えるプロジェクト（uv run ruff）。
#       uv を使わない場合は `ruff format "$file"` / `ruff check --fix "$file"` に書き換える。
set -euo pipefail

input=$(cat)
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""')

# .py 以外、または存在しないパスは何もしない
case "$file" in
  *.py) ;;
  *) exit 0 ;;
esac
[ -f "$file" ] || exit 0

# 整形 → lint 自動修正。失敗してもコミット前の pre-commit が最終ゲートなので握りつぶす。
uv run ruff format "$file" >/dev/null 2>&1 || true
uv run ruff check --fix "$file" >/dev/null 2>&1 || true
exit 0
