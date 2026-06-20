---
name: hook-status
description: |
  フック稼働状況の診断スキル。フックスクリプトの存在・ログ蓄積状況を確認してフェーズ判定を出力する。
  /hook-status で呼び出す。「フックが動いてるか確認して」でも自律発動。
---

# hook-status スキル

## 実行手順

Bash ツールで以下を順番に確認し、結果をフォーマットして出力する。

```bash
# 1. フックスクリプトの存在・サイズ確認
ls -la .claude/hooks/

# 2. settings.json の確認
cat .claude/settings.json

# 3. ログファイルの状態
ls -lh logs/ 2>/dev/null || echo "logs ディレクトリなし"

# 4. tool-audit.jsonl の最新 3 件
tail -3 logs/tool-audit.jsonl 2>/dev/null \
  | python3 -c "import sys,json; [print(json.dumps(json.loads(l), indent=2, ensure_ascii=False)) for l in sys.stdin]"

# 5. ブロック件数
wc -l logs/blocked.jsonl 2>/dev/null || echo "blocked.jsonl なし（正常）"
```

## 出力フォーマット

```
## フック稼働状況

### スクリプト
✅ _common.py        — 存在
✅ tool_logger.py    — 存在
✅ log_reminder.py   — 存在
⚠️  session_summary.py  — なし（Phase 2 未実装）
⚠️  pattern_detector.py — なし（Phase 2 未実装）

### ログ蓄積状況
✅ tool-audit.jsonl  — N 行（最終: YYYY-MM-DD HH:MM）
✅ blocked.jsonl     — N 件
❌ session-log.md    — なし

### 判定
Phase 1: ✅ 正常稼働中
Phase 2: ⏳ 未実装
```

スクリプトや設定が欠けている場合は、原因と対処手順を一緒に提示すること。
