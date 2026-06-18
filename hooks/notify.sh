#!/usr/bin/env bash
# Notification フック: Claude が入力待ち/確認待ちになったらデスクトップ通知する。
# 長時間タスク中に別作業で待つ用。
set -euo pipefail

msg=$(cat | jq -r '.message // "Claude が入力待ちです"')

# リポジトリ名をタイトルに使う（取得できなければ "Claude Code" にフォールバック）
repo=$(git rev-parse --show-toplevel 2>/dev/null | xargs basename 2>/dev/null || echo "Claude Code")
title="Claude Code · ${repo}"

# macOS
if command -v osascript >/dev/null 2>&1; then
  osascript -e "display notification \"$msg\" with title \"$title\"" >/dev/null 2>&1 || true
fi

# Linux (notify-send があれば)
if command -v notify-send >/dev/null 2>&1; then
  notify-send "$title" "$msg" || true
fi

exit 0
