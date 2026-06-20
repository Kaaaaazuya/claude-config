---
name: session-post
description: |
  ログ集計→学び整理→MDXブログ下書き生成をワンコマンドで実行するパイプラインスキル。
  セッション終了後に /session-post を実行するだけで drafts/ に MDX が生成される。
  途中の確認はタイトル・slug の1回のみ。
---

# session-post スキル

## 概要

以下の3段階をひと続きで実行する。各段階の詳細ロジックは対応スキルを参照。

```
STEP 1: 集計  — tool-audit.jsonl を分析してセッションの輪郭を掴む
STEP 2: 整理  — 記事にする価値がある学びを1つ選ぶ
STEP 3: 生成  — タイトル/slug を確認してから MDX を書き出す
```

---

## STEP 1: 集計

```bash
# 行数確認（10行未満は中断）
wc -l logs/tool-audit.jsonl 2>/dev/null || { echo "tool-audit.jsonl がありません。フック設定を確認してください。"; exit 1; }
```

行数が 10 未満なら「データが少なすぎます（現在 N 行）。もう少し作業してから実行してください。」と伝えて終了する。

`logs/tool-audit.jsonl` を Read して以下を集計する（Bash インラインスクリプト）:

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
errors = [e for e in entries if not e.get("success", True)]

print("=== ツール使用回数 ===")
for t, c in tool_counts.most_common():
    print(f"  {t}: {c}回")

print("\n=== 繰り返したコマンド（3回以上）===")
for cmd, c in cmd_counts.most_common(10):
    if c >= 3:
        print(f"  {c}回: {cmd[:80]}")

print(f"\n=== エラー: {len(errors)}/{len(entries)} 件 ===")
EOF
```

集計結果を内部で保持する（出力はしない）。

---

## STEP 2: 整理

STEP 1 の集計結果と現在の会話コンテキストを踏まえ、以下の問いに自分で答える:

1. このセッションで**最も非自明だった判断**は何か？
2. **試行錯誤して解決した問題**は何か？鍵は何だったか？
3. **次回も役立つ再現可能な手順**として言語化できるか？

上の3問を満たす学びを **1つだけ** 選ぶ（複数あっても絞る）。

選んだ学びを以下の形式で整理する（ユーザーには見せない、内部メモとして使う）:

```
課題: ...
鍵となった判断/手順: ...
再現手順の骨子:
  1. ...
  2. ...
```

整理した内容を `logs/retro-candidates.md` に追記する（既存があれば末尾に追加）:

```markdown
## {YYYY-MM-DD HH:MM} セッション振り返り

### {一行サマリー}
- **解決した課題**: ...
- **鍵となった判断/手順**: ...
- **再現手順の骨子**:
  1. ...
  2. ...
- **スキル化推奨度**: 高 / 中 / 低
```

---

## STEP 3: 生成

STEP 2 で選んだ学びをもとにタイトルと slug を決め、ユーザーに1回だけ確認する:

```
📝 以下の内容でMDXを生成します。修正があれば教えてください:

タイトル: {日本語タイトル}
slug:      {kebab-case-slug}
tags:      [{tag1}, {tag2}, ...]
保存先:    drafts/{YYYY-MM-DD}-{slug}.mdx

このまま生成しますか？
```

確認が取れたら以下のフォーマットで MDX を生成して Write で保存する:

````mdx
---
title: "{タイトル}"
date: {YYYY-MM-DD}
tags: [{tag1}, {tag2}]
draft: true
---

## はじめに

{解決した課題・背景を1〜2段落で。}

## 状況

{問題が起きた状況・環境・前提条件。}

## 詰まったポイント

{試行錯誤の内容・罠になった点。コードブロックを使う。}

```言語
{コード例}
```

## 解決策

{鍵となった判断・再現可能な手順。}

```言語
{コード例}
```

## まとめ

- {学び1}
- {学び2}
````

保存後、パスをユーザーに伝えて終了する。

---

## 中断条件

| 状況 | 対応 |
|------|------|
| `tool-audit.jsonl` がない | フック設定を確認するよう案内して終了 |
| 行数が 10 未満 | データ不足を伝えて終了 |
| 記事にする価値のある学びがない | 「今回は記事化できる学びが見つかりませんでした」と伝えて終了 |

## 品質チェック（保存前）

- `draft: true` が設定されているか
- 個人情報・プロジェクト固有の情報（パス・社名・顧客名）が含まれていないか
- コードブロックに言語識別子が付いているか
