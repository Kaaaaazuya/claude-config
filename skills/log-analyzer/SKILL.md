---
name: log-analyzer
description: |
  ログ分析・パターン抽出スキル。logs/tool-audit.jsonl を読んで繰り返しパターン・
  エラー傾向・スキル化候補を特定し、分析レポートを生成する。
  「ログ分析して」「パターン調べて」「何が多い?」で自律発動。
  /log-analyzer でも呼び出せる。
---

# log-analyzer スキル

## 前提確認

実行前に以下を確認すること:

```bash
wc -l logs/tool-audit.jsonl 2>/dev/null || echo "ファイルなし"
```

行数が 10 未満の場合は「データ不足のため分析できません（現在 N 行）」と伝えて終了する。

## 実行手順

1. `logs/tool-audit.jsonl` を Read で読み込む

2. Bash で集計する:

```bash
python3 - << 'EOF'
import json
from pathlib import Path
from collections import Counter

lines = Path("logs/tool-audit.jsonl").read_text().splitlines()
entries = [json.loads(l) for l in lines if l.strip()]

tool_counts = Counter(e["tool"] for e in entries)
cmd_counts = Counter(
    e["input"].get("command", "")
    for e in entries if e.get("tool") == "Bash" and e.get("input")
)
error_entries = [e for e in entries if not e.get("success", True)]

print("=== ツール使用回数 ===")
for t, c in tool_counts.most_common(10):
    print(f"{t}: {c}回")

print("\n=== Bash コマンド（3 回以上）===")
for cmd, c in cmd_counts.most_common(20):
    if c >= 3:
        print(f"{c}回: {cmd[:80]}")

print(f"\n=== エラー数: {len(error_entries)} / {len(entries)} 件 ===")
for e in error_entries[:5]:
    print(f"  [{e['tool']}] exit={e.get('exit_code')} | {str(e.get('input', ''))[:60]}")
EOF
```

3. 以下のフォーマットでレポートを組み立てる:

```markdown
## ログ分析レポート {YYYY-MM-DD}

### 分析サマリー
- 総ツール呼び出し: N 件（期間: {最古 ts} 〜 {最新 ts}）
- エラー率: X%

### 繰り返しパターン（スキル候補）
| コマンド | 回数 | アクション |
|---------|------|-----------|
| xxx     | N 回  | /skill-builder でスキル化を検討 |

### エラー多発箇所
| ツール | 回数 | 直近エラー |
|-------|------|----------|

### 推奨アクション
- [ ] N 回以上繰り返したコマンドをスキル化（/skill-builder）
- [ ] 頻出エラーを CLAUDE.md の禁止パターンに追加
```

4. レポートを `logs/analysis-{YYYY-MM-DD}.md` に Write で保存する

5. CLAUDE.md の「自動学習セクション」の更新を提案する（確認を取ってから実行すること）
